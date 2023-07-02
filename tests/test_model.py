from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, cast
from xml.dom import minidom
from xml.etree import ElementTree

import pytest
import xmlschema
from pydantic import ValidationError

import ome_types
from ome_types import from_tiff, from_xml, model, to_xml

if TYPE_CHECKING:
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
    assert from_xml(valid_xml, validate=validate)


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


def test_roundtrip(valid_xml: Path) -> None:
    """Ensure we can losslessly round-trip XML through the model and back."""
    if true_stem(valid_xml) in SKIP_ROUNDTRIP:
        pytest.xfail("known issues with canonicalization")

    xml = str(valid_xml)

    original = _canonicalize(xml, True)
    ome = from_xml(xml)
    rexml = to_xml(ome)
    new = _canonicalize(rexml, True)
    if new != original:
        Path("original.xml").write_text(original)
        Path("rewritten.xml").write_text(new)
        raise AssertionError


def test_roundtrip_inverse(valid_xml: Path, tmp_path: Path) -> None:
    """both variants have been touched by the model, here..."""
    ome1 = from_xml(valid_xml)

    xml = to_xml(ome1)
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


# ########## Canonicalization utils ##########


@lru_cache(maxsize=None)
def _get_schema() -> xmlschema.XMLSchema:
    schema = xmlschema.XMLSchema(OME_2016_06_XSD)
    # FIXME Hack to work around xmlschema poor support for keyrefs to
    # substitution groups
    ls_sgs = schema.maps.substitution_groups[f"{NS_OME}LightSourceGroup"]
    ls_id_maps = schema.maps.identities[f"{NS_OME}LightSourceIDKey"]
    ls_id_maps.elements = {e: None for e in ls_sgs}
    return schema


def _sort_elements(element, recursive=True):
    # Sort the child elements alphabetically by their tag name
    sorted_children = sorted(element, key=lambda child: child.tag)

    # Replace the existing child elements with the sorted ones
    element[:] = sorted_children

    # Recursively sort child elements for each subelement
    if recursive:
        for child in element:
            _sort_elements(child)


def _add_defaults(xml: str) -> ElementTree.Element:
    # we use xmlschema to encode then decode the xml to add missing
    # default values for the sake of canonicalization
    # this is the ONLY remaining thing that xmlschema is used for
    # (and only in testing).

    schema = _get_schema()
    d = cast(dict, schema.decode(xml, use_defaults=True))
    # Strip extra whitespace in the schemaLocation value.
    d["@xsi:schemaLocation"] = re.sub(r"\s+", " ", d["@xsi:schemaLocation"])
    return schema.encode(d, path=NS_OME + "OME", use_defaults=True)  # type: ignore


def _canonicalize(xml: str, strip_empty: bool) -> str:
    root = _add_defaults(xml)

    # These are the tags that appear in the example files with empty
    # content. Since our round-trip will drop empty elements, we'll need to
    # strip them from the "original" documents before comparison.
    if strip_empty:
        for tag in ("Description", "LightPath", "Map"):
            for e in root.findall(f".//{NS_OME}{tag}[.='']..."):
                e.remove(e.find(f"{NS_OME}{tag}"))  # type: ignore

    # ET.canonicalize can't handle an empty namespace so we need to
    # re-register the OME namespace with an actual name before calling
    # tostring.
    _sort_elements(root)

    ElementTree.register_namespace("ome", URI_OME)
    xml_out = ElementTree.tostring(root, "unicode")
    xml_out = ElementTree.canonicalize(xml_out, strip_text=True)
    xml_out = minidom.parseString(xml_out).toprettyxml(indent="  ")
    return xml_out
