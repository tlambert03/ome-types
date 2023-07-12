from __future__ import annotations

import datetime
import io
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from ome_types import from_tiff, from_xml, model, to_xml
from ome_types._conversion import OME_2016_06_URI, _get_root_ome_type

DATA = Path(__file__).parent / "data"
VALIDATE = [False]


@pytest.mark.parametrize("validate", VALIDATE)
def test_from_valid_xml(valid_xml: Path, validate: bool) -> None:
    ome = model.OME.from_xml(valid_xml, validate=validate)  # class method for coverage
    assert ome
    assert repr(ome)


@pytest.mark.parametrize("validate", VALIDATE)
def test_from_invalid_xml(invalid_xml: Path, validate: bool) -> None:
    if validate:
        with pytest.raises(ValidationError):
            from_xml(invalid_xml, validate=validate)
    else:
        with pytest.warns():
            from_xml(invalid_xml, validate=validate)


@pytest.mark.parametrize("validate", VALIDATE)
def test_from_tiff(validate: bool) -> None:
    """Test that OME metadata extractions from Tiff headers works."""
    _path = DATA / "ome.tiff"
    ome = from_tiff(_path, validate=validate)
    assert len(ome.images) == 1
    assert ome.images[0].id == "Image:0"
    assert ome.images[0].pixels.size_x == 6
    assert ome.images[0].pixels.channels[0].samples_per_pixel == 1

    with open(_path, "rb") as fh:
        assert model.OME.from_tiff(fh) == ome  # class method for coverage


def test_no_id() -> None:
    """Test that ids are optional, and auto-increment."""
    i = model.Instrument(id=20)  # type: ignore
    assert i.id == "Instrument:20"
    i2 = model.Instrument()  # type: ignore
    assert i2.id == "Instrument:21"

    # but validation still works
    with pytest.warns(match="Casting invalid InstrumentID"):
        model.Instrument(id="nonsense")


def test_required_missing() -> None:
    """Test subclasses with non-default arguments still work."""
    with pytest.raises(ValidationError, match="value\n  field required"):
        model.BooleanAnnotation()  # type: ignore

    with pytest.raises(ValidationError, match="x\n  field required"):
        model.Label()  # type: ignore


def test_refs() -> None:
    xml = DATA / "two-screens-two-plates-four-wells.ome.xml"
    ome = from_xml(xml)
    assert ome.screens[0].plate_refs[0].ref is ome.plates[0]


def test_with_ome_ns() -> None:
    assert from_xml(DATA / "ome_ns.ome.xml").experimenters


def test_get_root_ome_type() -> None:
    xml = io.BytesIO(f'<Image xmlns="{OME_2016_06_URI}" />'.encode())
    t = _get_root_ome_type(xml)
    assert t is model.Image

    xml = io.BytesIO(f'<ome:Image xmlns:ome="{OME_2016_06_URI}" />'.encode())
    t = _get_root_ome_type(xml)
    assert t is model.Image

    with pytest.raises(ValueError, match="Unknown root element"):
        _get_root_ome_type(io.BytesIO(b"<Imdgage />"))

    # this can be used to instantiate XML with a non OME root type:
    obj = from_xml(f'<Project xmlns="{OME_2016_06_URI}" />')
    assert isinstance(obj, model.Project)
    obj = from_xml(
        f'<XMLAnnotation xmlns="{OME_2016_06_URI}"><Value><Data>'
        "</Data></Value></XMLAnnotation>"
    )
    assert isinstance(obj, model.XMLAnnotation)


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
