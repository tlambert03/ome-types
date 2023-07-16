from __future__ import annotations

import io
from pathlib import Path

import pytest
from pydantic import ValidationError

from ome_types import from_xml, model
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


def test_unknown_ns():
    with pytest.raises(ValueError, match="Unsupported document namespace"):
        from_xml('<Image xmlns="http://unknown.org" />')
