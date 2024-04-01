from __future__ import annotations

import json
import pickle
import re
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, cast
from xml.dom import minidom
from xml.etree import ElementTree as ET

import pytest
from some_types import from_xml, to_dict, to_xml
from some_types._conversion import SOME_2016_06_NS, SOME_2016_06_URI, SOME_2016_06_XSD
from some_types.model import SOME, Channel, Image, Pixels

if TYPE_CHECKING:
    import xmlschema

DATA = Path(__file__).parent / "data"
SKIP_ROUNDTRIP = {
    # These have XMLAnnotations with extra namespaces and mixed content, which
    # the automated round-trip test code doesn't properly verify yet. So even
    # though these files do appear to round-trip correctly when checked by eye,
    # we'll play it safe and skip them until the test is fixed.
    "spim",
    "xmlannotation-multi-value",
    "xmlannotation-svg",
    # we don't roundtrip older versions of the schema
    "2008_instrument",
    "seq0000xy01c1",
}


def true_stem(p: Path) -> str:
    return p.name.partition(".")[0]


@pytest.mark.parametrize("channel_kwargs", [{}, {"color": "blue"}])
def test_color_unset(channel_kwargs: dict) -> None:
    some = SOME(
        images=[
            Image(
                pixels=Pixels(
                    size_c=1,
                    size_t=1,
                    size_x=1,
                    size_y=1,
                    size_z=1,
                    dimension_order="XYZTC",
                    type="uint16",
                    channels=[Channel(**channel_kwargs)],
                )
            )
        ]
    )

    assert ("Color" in some.to_xml()) is bool(channel_kwargs)


def test_serialization(valid_xml: Path) -> None:
    """Test pickle serialization and reserialization."""
    some = from_xml(valid_xml)
    serialized = pickle.dumps(some)
    deserialized = pickle.loads(serialized)
    assert some == deserialized


def test_dict_roundtrip(valid_xml: Path) -> None:
    # Test round-trip through to_dict and from_dict
    some1 = from_xml(valid_xml)
    some2 = SOME(**to_dict(some1))
    assert some1 == some2


def test_xml_roundtrip(valid_xml: Path) -> None:
    """Ensure we can losslessly round-trip XML through the model and back."""
    if true_stem(valid_xml) in SKIP_ROUNDTRIP:
        pytest.xfail("known issues with canonicalization")

    original = _canonicalize(valid_xml.read_bytes())

    some = from_xml(valid_xml)
    rexml = to_xml(some, validate=True)
    new = _canonicalize(rexml)
    if new != original:
        Path("original.xml").write_text(original)
        Path("rewritten.xml").write_text(new)
        raise AssertionError


def test_xml_roundtrip_inverse(valid_xml: Path, tmp_path: Path) -> None:
    """when xml->SOME1->xml->SOME2,  assert SOME1 == SOME2.

    both variants have been touched by the model, here.
    """
    some1 = from_xml(valid_xml)

    # FIXME:
    # there is a small difference in the XML output when using xml instead of lxml
    # that makes the text of an xml annotation in `xmlannotation-multi-value` be
    # 'B\n          ' instead of 'B'.
    # we should investigate this and fix it, but here we just use indent=0 to avoid it.
    xml = to_xml(some1, indent=0)
    out = tmp_path / "test.xml"
    out.write_bytes(xml.encode())
    some2 = from_xml(out)

    assert some1 == some2


# ########## Canonicalization utils for testing ##########


def _canonicalize(xml: str | bytes, pretty: bool = False) -> str:
    ET.register_namespace("some", SOME_2016_06_URI)

    # The only reason we're using xmlschema at this point is because
    # it converts floats properly CutIn="550" -> CutIn="550.0" based on the schema
    # once that is fixed, we can remove xmlschema entirely
    schema = _get_schema()
    decoded = schema.decode(xml)
    root = cast(ET.Element, schema.encode(decoded, path=f"{SOME_2016_06_NS}SOME"))

    # Strip extra whitespace in the schemaLocation value.
    SCHEMA_LOCATION = "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"
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

    schema = xmlschema.XMLSchema(SOME_2016_06_XSD)
    # FIXME Hack to work around xmlschema poor support for keyrefs to
    # substitution groups.  This can be removed, if decode(validation='skip') is used.
    ls_sgs = schema.maps.substitution_groups[f"{SOME_2016_06_NS}LightSourceGroup"]
    ls_id_maps = schema.maps.identities[f"{SOME_2016_06_NS}LightSourceIDKey"]
    ls_id_maps.elements = {e: None for e in ls_sgs}
    return schema


def _sort_elements(element: ET.Element, recursive: bool = True) -> None:
    # Replace the existing child elements with the sorted ones
    element[:] = sorted(element, key=lambda child: child.tag)

    if recursive:
        # Recursively sort child elements for each subelement
        for child in element:
            _sort_elements(child)


def test_canonicalize() -> None:
    pytest.importorskip("lxml")
    some = from_xml(DATA / "example.some.xml", validate=True)
    _ = to_xml(some, validate=True, canonicalize=True)


def test_export_schema() -> None:
    schema = SOME.model_json_schema()
    assert isinstance(schema, dict)
    assert isinstance(json.dumps(schema), str)
