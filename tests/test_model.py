from __future__ import annotations

import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from ome_types import from_tiff, from_xml, model
from ome_types._conversion import _get_ome_type

DATA = Path(__file__).parent / "data"
VALIDATE = [False]


@pytest.mark.parametrize("validate", VALIDATE)
def test_from_valid_xml(valid_xml: Path, validate: bool) -> None:
    ome = from_xml(valid_xml, validate=validate)
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


def test_get_ome_type() -> None:
    URI_OME = "http://www.openmicroscopy.org/Schemas/OME/2016-06"

    t = _get_ome_type(f'<Image xmlns="{URI_OME}" />')
    assert t is model.Image

    with pytest.raises(ValueError):
        _get_ome_type("<Image />")

    # this can be used to instantiate XML with a non OME root type:
    project = from_xml(f'<Project xmlns="{URI_OME}" />')
    assert isinstance(project, model.Project)


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
