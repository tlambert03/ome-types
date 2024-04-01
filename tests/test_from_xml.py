from __future__ import annotations

import io
from pathlib import Path

import pytest
from pydantic import ValidationError
from some_types import from_xml, model
from some_types._conversion import SOME_2016_06_URI, _get_root_some_type

DATA = Path(__file__).parent / "data"
VALIDATE = [False]


@pytest.mark.parametrize("validate", VALIDATE)
def test_from_valid_xml(valid_xml: Path, validate: bool) -> None:
    some = model.SOME.from_xml(
        valid_xml, validate=validate
    )  # class method for coverage
    assert some
    assert repr(some)


@pytest.mark.parametrize("validate", VALIDATE)
def test_from_invalid_xml(invalid_xml: Path, validate: bool) -> None:
    if validate:
        with pytest.raises(ValidationError):
            from_xml(invalid_xml, validate=validate)
    else:
        with pytest.warns():
            from_xml(invalid_xml, validate=validate)


def test_with_some_ns() -> None:
    assert from_xml(DATA / "some_ns.some.xml").experimenters


def test_get_root_some_type() -> None:
    xml = io.BytesIO(f'<Image xmlns="{SOME_2016_06_URI}" />'.encode())
    t = _get_root_some_type(xml)
    assert t is model.Image

    xml = io.BytesIO(f'<some:Image xmlns:ome="{SOME_2016_06_URI}" />'.encode())
    t = _get_root_some_type(xml)
    assert t is model.Image

    with pytest.raises(ValueError, match="Unknown root element"):
        _get_root_some_type(io.BytesIO(b"<Imdgage />"))

    # this can be used to instantiate XML with a non SOME root type:
    obj = from_xml(f'<Project xmlns="{SOME_2016_06_URI}" />')
    assert isinstance(obj, model.Project)
    obj = from_xml(
        f'<XMLAnnotation xmlns="{SOME_2016_06_URI}"><Value><Data>'
        "</Data></Value></XMLAnnotation>"
    )
    assert isinstance(obj, model.XMLAnnotation)


def test_unknown_ns() -> None:
    with pytest.raises(ValueError, match="Unsupported document namespace"):
        from_xml('<Image xmlns="http://unknown.org" />')


def test_uncapitalized_ns() -> None:
    xml = '<Detector xmlns="http://www.openmicroscopy.org/Schemas/ome/2016-06" />'
    some = from_xml(xml)
    assert isinstance(some, model.Detector)


def test_weird_input() -> None:
    with pytest.raises(ValueError, match="Could not parse XML"):
        from_xml("ImageJmetadata")


def test_must_be_binary(tmp_path: Path) -> None:
    xml = tmp_path / "test.xml"
    xml.write_text('<SOME xmlns="http://www.openmicroscopy.org/Schemas/ome/2016-06" />')

    with open(xml, "rb") as fh:
        assert isinstance(from_xml(fh), model.SOME)

    with open(xml) as fh, pytest.raises(TypeError, match="must be opened in binary"):
        from_xml(fh)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="Unsupported source type"):
        from_xml(8)  # type: ignore[arg-type]
