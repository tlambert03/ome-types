from __future__ import annotations

import datetime
import re
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, cast
from xml.dom import minidom
from xml.etree import ElementTree as ET

import pytest
from pydantic import ValidationError

import ome_types
from ome_types import from_tiff, from_xml, model, to_xml
from ome_types._conversion import _get_ome_type

if TYPE_CHECKING:
    import xmlschema
    from _pytest.mark.structures import ParameterSet

TESTS = Path(__file__).parent
DATA = TESTS / "data"

SHOULD_FAIL_VALIDATION = {"invalid_xml_annotation", "bad"}
SHOULD_FAIL_ROUNDTRIP = {
    # Order of elements in StructuredAnnotations and Union are jumbled.
    "timestampannotation-posix-only",
    "transformations-downgrade",
    "invalid_xml_annotation",
}

SKIP_ROUNDTRIP = {
    # These have XMLAnnotations with extra namespaces and mixed content, which
    # the automated round-trip test code doesn't properly verify yet. So even
    # though these files do appear to round-trip correctly when checked by eye,
    # we'll play it safe and skip them until the test is fixed.
    "spim",
    "xmlannotation-multi-value",
    "xmlannotation-svg",
}

URI_OME = "http://www.openmicroscopy.org/Schemas/OME/2016-06"
SCHEMA_LOCATION = "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"
NS_OME = "{" + URI_OME + "}"
OME_2016_06_XSD = str(Path(ome_types.__file__).parent / "ome-2016-06.xsd")


def true_stem(p: Path) -> str:
    return p.name.partition(".")[0]


all_xml = list(DATA.glob("*.ome.xml"))
xml_roundtrip: list[Path | ParameterSet] = []
for f in all_xml:
    stem = true_stem(f)
    if stem in SHOULD_FAIL_ROUNDTRIP:
        mrk = pytest.mark.xfail(strict=True, reason="Unexpected success. You fixed it!")
        f = pytest.param(f, marks=mrk)  # type: ignore
    elif stem in SKIP_ROUNDTRIP:
        f = pytest.param(f, marks=pytest.mark.skip)  # type: ignore
    xml_roundtrip.append(f)


validate = [False]


@pytest.mark.parametrize("validate", validate)
def test_from_valid_xml(valid_xml: Path, validate: bool) -> None:
    ome = from_xml(valid_xml, validate=validate)
    assert ome
    assert repr(ome)


@pytest.mark.parametrize("validate", validate)
def test_from_invalid_xml(invalid_xml: Path, validate: bool) -> None:
    if validate:
        with pytest.raises(ValidationError):
            from_xml(invalid_xml, validate=validate)
    else:
        with pytest.warns():
            from_xml(invalid_xml, validate=validate)


@pytest.mark.parametrize("validate", validate)
def test_from_tiff(validate: bool) -> None:
    """Test that OME metadata extractions from Tiff headers works."""
    _path = DATA / "ome.tiff"
    ome = from_tiff(_path, validate=validate)
    assert len(ome.images) == 1
    assert ome.images[0].id == "Image:0"
    assert ome.images[0].pixels.size_x == 6
    assert ome.images[0].pixels.channels[0].samples_per_pixel == 1


def test_roundtrip_inverse(valid_xml: Path, tmp_path: Path) -> None:
    """both variants have been touched by the model, here..."""
    ome1 = from_xml(valid_xml)

    # FIXME:
    # there is a small difference in the XML output when using xml instead of lxml
    # that makes the text of an xml annotation in `xmlannotation-multi-value` be
    # 'B\n          ' instead of 'B'.
    # we should investigate this and fix it, but here we just use indent=0 to avoid it.
    xml = to_xml(ome1, indent=0)
    out = tmp_path / "test.xml"
    out.write_bytes(xml.encode())
    ome2 = from_xml(out)

    assert ome1 == ome2


# @pytest.mark.parametrize("validate", validate)
# def test_to_xml_with_kwargs(validate):
#     """Ensure kwargs are passed to ElementTree"""
#     ome = from_xml(DATA / "example.ome.xml", validate=validate)

#     with mock.patch("xml.etree.ElementTree.tostring") as mocked_et_tostring:
#         element = to_xml_element(ome)
#         # Use an ElementTree.tostring kwarg and assert that it was passed through
#         to_xml(element, xml_declaration=True)
#         assert mocked_et_tostring.call_args.xml_declaration


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
    t = _get_ome_type(f'<Image xmlns="{URI_OME}" />')
    assert t is model.Image

    with pytest.raises(ValueError):
        _get_ome_type("<Image />")

    # this can be used to instantiate XML with a non OME root type:
    project = from_xml(f'<Project xmlns="{URI_OME}" />')
    assert isinstance(project, model.Project)


def test_roundtrip(valid_xml: Path) -> None:
    """Ensure we can losslessly round-trip XML through the model and back."""
    if true_stem(valid_xml) in SKIP_ROUNDTRIP:
        pytest.xfail("known issues with canonicalization")

    original = _canonicalize(valid_xml.read_bytes())

    ome = from_xml(valid_xml)
    rexml = to_xml(ome)
    new = _canonicalize(rexml)
    if new != original:
        Path("original.xml").write_text(original)
        Path("rewritten.xml").write_text(new)
        raise AssertionError


# ########## Canonicalization utils for testing ##########


def _canonicalize(xml: str | bytes, pretty: bool = False) -> str:
    ET.register_namespace("ome", URI_OME)

    # The only reason we're using xmlschema at this point is because
    # it converts floats properly CutIn="550" -> CutIn="550.0" based on the schema
    # once that is fixed, we can remove xmlschema entirely
    schema = _get_schema()
    decoded = schema.decode(xml)
    root = cast(ET.Element, schema.encode(decoded, path=f"{NS_OME}OME"))

    # Strip extra whitespace in the schemaLocation value.
    root.attrib[SCHEMA_LOCATION] = re.sub(r"\s+", " ", root.attrib[SCHEMA_LOCATION])

    # sorting elements actually breaks the validity of some documents,
    # but it's useful for comparison sake.
    _sort_elements(root)
    xml_out = ET.tostring(root, "unicode")
    xml_out = ET.canonicalize(xml_out, strip_text=True)
    if pretty:
        # totally optional for comparison sake... but nice for debugging
        xml_out = minidom.parseString(xml_out).toprettyxml(indent="  ")
    return xml_out


@lru_cache(maxsize=None)
def _get_schema() -> xmlschema.XMLSchemaBase:
    xmlschema = pytest.importorskip("xmlschema")

    schema = xmlschema.XMLSchema(OME_2016_06_XSD)
    # FIXME Hack to work around xmlschema poor support for keyrefs to
    # substitution groups.  This can be removed, if decode(validation='skip') is used.
    ls_sgs = schema.maps.substitution_groups[f"{NS_OME}LightSourceGroup"]
    ls_id_maps = schema.maps.identities[f"{NS_OME}LightSourceIDKey"]
    ls_id_maps.elements = {e: None for e in ls_sgs}
    return schema


def _sort_elements(element: ET.Element, recursive: bool = True) -> None:
    # Replace the existing child elements with the sorted ones
    element[:] = sorted(element, key=lambda child: child.tag)

    if recursive:
        # Recursively sort child elements for each subelement
        for child in element:
            _sort_elements(child)


def test_datetimes() -> None:
    model.TimestampAnnotation(value=datetime.datetime.now())
