from __future__ import annotations

import copy
import datetime
import io
import sys
import warnings
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError
from pydantic_compat import PYDANTIC2

from ome_types import from_tiff, from_xml, model, to_xml
from ome_types.model import OME, AnnotationRef, CommentAnnotation, Instrument

DATA = Path(__file__).parent / "data"


def test_from_tiff() -> None:
    """Test that OME metadata extractions from Tiff headers works."""
    _path = DATA / "ome.tiff"
    ome = from_tiff(_path)
    assert len(ome.images) == 1
    assert ome.images[0].id == "Image:0"
    assert ome.images[0].pixels.size_x == 6
    assert ome.images[0].pixels.channels[0].samples_per_pixel == 1

    with open(_path, "rb") as fh:
        assert model.OME.from_tiff(fh) == ome  # class method for coverage


def test_required_missing() -> None:
    """Test subclasses with non-default arguments still work."""
    with pytest.raises(ValidationError, match="required"):
        model.BooleanAnnotation()  # type: ignore

    with pytest.raises(ValidationError, match="required"):
        model.Label()  # type: ignore


def test_refs() -> None:
    xml = DATA / "two-screens-two-plates-four-wells.ome.xml"
    ome = from_xml(xml)
    assert ome.screens[0].plate_refs[0].ref is ome.plates[0]


@pytest.mark.skipif(not PYDANTIC2, reason="pydantic v1 has poor support for deepcopy")
def test_ref_copy() -> None:
    aref = AnnotationRef(id=1)
    ome = OME(
        instruments=[Instrument(annotation_refs=[aref])],
        structured_annotations=[CommentAnnotation(id=1, value="test")],
    )
    assert ome.instruments[0].annotation_refs[0] is aref
    assert aref._ref is not None
    ome2 = ome.model_copy(deep=True)
    assert ome2.instruments[0].annotation_refs[0].ref is not aref.ref

    ome3 = copy.deepcopy(ome)
    assert ome3.instruments[0].annotation_refs[0].ref is not aref.ref
    ome4 = OME(**ome.dict())
    assert ome4.instruments[0].annotation_refs[0].ref is not aref.ref

    del ome, aref
    assert ome2.instruments[0].annotation_refs[0].ref is not None
    assert ome3.instruments[0].annotation_refs[0].ref is not None
    assert ome4.instruments[0].annotation_refs[0].ref is not None


def test_datetimes() -> None:
    now = datetime.datetime.now()
    anno = model.TimestampAnnotation(value=now)
    assert anno.value == now
    anno = model.TimestampAnnotation(value="0066-07-18T00:00:00")
    assert anno.value == datetime.datetime(66, 7, 18)

    XML = """<?xml version="1.0" ?>
    <TimestampAnnotation  xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06"
        ID="Annotation:11" Namespace="sample.openmicroscopy.org/time/dinosaur">
      <Value>-231400000-01-01T00:00:00</Value>
    </TimestampAnnotation>
    """
    with pytest.warns(match="Invalid datetime.*BC dates are not supported"):
        from_xml(XML)


@pytest.mark.parametrize("only", [True, False, {}, None])
def test_metadata_only(only: bool) -> None:
    pix = model.Pixels(
        metadata_only=only,  # passing bool should be fine
        size_c=1,
        size_t=1,
        size_x=1,
        size_y=1,
        size_z=1,
        dimension_order="XYZCT",
        type="uint8",
    )
    if only not in (False, None):  # note that empty dict is "truthy" for metadata_only
        assert pix.metadata_only
    else:
        assert not pix.metadata_only


def test_deepcopy() -> None:
    from copy import deepcopy

    ome = from_xml(DATA / "example.ome.xml")
    newome = deepcopy(ome)

    assert ome == newome
    assert ome is not newome


def test_structured_annotations() -> None:
    long = model.LongAnnotation(value=1)
    annotations = [model.CommentAnnotation(value="test comment"), long]
    ome = model.OME(structured_annotations=annotations)
    assert ome
    assert len(ome.structured_annotations) == 2
    assert "Long" in ome.to_xml()
    ome.structured_annotations.remove(long)
    assert "Long" not in ome.to_xml()

    assert list(ome.structured_annotations) == ome.structured_annotations


def test_colors() -> None:
    from ome_types.model.simple_types import Color

    shape = model.Shape(fill_color="red", stroke_color="blue")
    assert isinstance(shape.fill_color, Color)
    assert isinstance(shape.stroke_color, Color)
    assert shape.fill_color.as_rgb_tuple() == (255, 0, 0)
    assert shape.stroke_color.as_named() == "blue"

    assert model.Shape().fill_color is None
    assert model.Shape().stroke_color is None


def test_xml_annotation() -> None:
    from xsdata_pydantic_basemodel.compat import AnyElement

    raw_xml = '<Data><Params A="1" B="2" C="3"/></Data>'
    xml_ann = model.XMLAnnotation(description="Some description", value=raw_xml)
    assert xml_ann.description == "Some description"
    assert isinstance(xml_ann.value, model.XMLAnnotation.Value)
    assert isinstance(xml_ann.value.any_elements[0], AnyElement)

    assert raw_xml in to_xml(xml_ann, indent=0)


XML = """
<OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06">
<Image ID="Image:0">
    <AcquisitionDate>2020-09-08T17:26:16.769000000</AcquisitionDate>
    <Pixels DimensionOrder="XYCTZ" Type="uint8" SizeC="1" SizeT="1"
            SizeX="18" SizeY="24" SizeZ="5">
    </Pixels>
</Image>
</OME>
"""


def test_bad_date() -> None:
    """Test that dates with too many microseconds are handled gracefully."""

    obj = from_xml(XML)
    assert obj.images[0].acquisition_date.microsecond == 769000  # type: ignore


@pytest.mark.parametrize(
    "source_type", ["path", "str_path", "str", "bytes", "stream", "handle"]
)
def test_source_types(source_type: str, single_xml: Path) -> None:
    if source_type == "path":
        xml: Any = single_xml
    elif source_type == "str_path":
        xml = str(single_xml)
    elif source_type == "str":
        xml = single_xml.read_text(encoding="utf-8")
    elif source_type == "bytes":
        xml = single_xml.read_bytes()
    elif source_type == "stream":
        xml = io.BytesIO(single_xml.read_bytes())
    elif source_type == "handle":
        xml = open(single_xml, "rb")
    assert isinstance(from_xml(xml), model.OME)


def test_numpy_pixel_types() -> None:
    numpy = pytest.importorskip("numpy")

    for m in model.PixelType:
        numpy.dtype(m.numpy_dtype)


def test_xml_annotations_to_etree(with_xml_annotations: Path) -> None:
    from xsdata_pydantic_basemodel.compat import AnyElement

    try:
        from lxml.etree import _Element as Elem
    except ImportError:
        from xml.etree.ElementTree import Element as Elem  # type: ignore

    ome = from_xml(with_xml_annotations)
    for anno in ome.structured_annotations:
        if isinstance(anno, model.XMLAnnotation):
            for elem in anno.value.any_elements:
                assert isinstance(elem, AnyElement)
                assert isinstance(elem.to_etree_element(), Elem)


def test_update_unset(pixels: model.Pixels) -> None:
    """Make sure objects appended to mutable sequences are included in the xml."""
    ome = model.OME()
    pixels.channels.extend([model.Channel(), model.Channel()])
    img = model.Image(pixels=pixels)
    ome.projects.append(model.Project())
    ome.datasets.append(model.Dataset())
    ome.images.append(img)
    ome.structured_annotations.append(model.CommentAnnotation(value="test"))

    xml = ome.to_xml(exclude_unset=True)
    assert "Pixels" in xml
    assert "Channel" in xml
    assert "Image" in xml
    assert "CommentAnnotation" in xml

    assert from_xml(xml) == ome


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
def test_transformations() -> None:
    from ome_types import etree_fixes

    # should not warn
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        # this is needed for xsdata usage of private typing attribute
        if sys.version_info >= (3, 13):
            warnings.simplefilter("ignore", DeprecationWarning)
        from_xml(DATA / "MMStack.ome.xml", transformations=etree_fixes.ALL_FIXES)

    # SHOULD warn
    with pytest.warns(match="Casting invalid"):
        from_xml(DATA / "MMStack.ome.xml")


def test_map_annotations() -> None:
    from ome_types.model import Map, MapAnnotation

    data = {"a": "string", "b": 2}

    # can be created from a dict
    map_annotation = MapAnnotation(value=data)
    map_val = map_annotation.value
    assert isinstance(map_annotation, MapAnnotation)
    assert isinstance(map_val, Map)

    out = map_annotation.value.model_dump()
    assert out == {k: str(v) for k, v in data.items()}  # all values cast to str

    # it's a mutable mapping
    map_val["c"] = "new"
    assert map_val.get("c") == "new"
    assert map_val.get("X") is None
    assert len(map_val) == 3
    assert set(map_val) == {"a", "b", "c"}
    assert dict(map_val) == map_val.model_dump() == {**out, "c": "new"}
    del map_val["c"]
    assert len(map_val) == 2

    _ = map_annotation.to_xml()  # shouldn't fail

    # only strings are allowed as values
    data["nested"] = [1, 2]
    with pytest.raises(ValidationError):
        MapAnnotation(value=data)
