import pickle
import re
from pathlib import Path
from unittest import mock
from xml.dom import minidom
from xml.etree import ElementTree

import pytest
import util
from pydantic import ValidationError
from xmlschema.validators.exceptions import XMLSchemaValidationError

from ome_types import from_tiff, from_xml, model, to_xml
from ome_types.schema import NS_OME, URI_OME, get_schema, to_xml_element

SHOULD_FAIL_READ = {
    # Some timestamps have negative years which datetime doesn't support.
    "timestampannotation",
}
SHOULD_RAISE_READ = {"bad"}
SHOULD_FAIL_ROUNDTRIP = {
    # Order of elements in StructuredAnnotations and Union are jumbled.
    "timestampannotation-posix-only",
    "transformations-downgrade",
}
SKIP_ROUNDTRIP = set()


def mark_xfail(fname):
    return pytest.param(
        fname,
        marks=pytest.mark.xfail(
            strict=True, reason="Unexpected success. You fixed it!"
        ),
    )


def mark_skip(fname):
    return pytest.param(fname, marks=pytest.mark.skip)


def true_stem(p):
    return p.name.partition(".")[0]


all_xml = list((Path(__file__).parent / "data").glob("*.ome.xml"))
xml_read = [mark_xfail(f) if true_stem(f) in SHOULD_FAIL_READ else f for f in all_xml]
xml_roundtrip = []
for f in all_xml:
    stem = true_stem(f)
    if stem in SHOULD_FAIL_READ | SHOULD_RAISE_READ:
        continue
    elif stem in SHOULD_FAIL_ROUNDTRIP:
        f = mark_xfail(f)
    elif stem in SKIP_ROUNDTRIP:
        f = mark_skip(f)
    xml_roundtrip.append(f)


@pytest.mark.parametrize("xml", xml_read, ids=true_stem)
def test_from_xml(xml, benchmark):

    if true_stem(xml) in SHOULD_RAISE_READ:
        with pytest.raises(XMLSchemaValidationError):
            assert benchmark(from_xml, xml)
    else:
        assert benchmark(from_xml, xml)


def test_from_tiff(benchmark):
    """Test that OME metadata extractions from Tiff headers works."""
    _path = Path(__file__).parent / "data" / "ome.tiff"
    ome = benchmark(from_tiff, _path)
    assert len(ome.images) == 1
    assert ome.images[0].id == "Image:0"
    assert ome.images[0].pixels.size_x == 6
    assert ome.images[0].pixels.channels[0].samples_per_pixel == 1


@pytest.mark.parametrize("xml", xml_roundtrip, ids=true_stem)
def test_roundtrip(xml, benchmark):
    """Ensure we can losslessly round-trip XML through the model and back."""
    xml = str(xml)
    schema = get_schema(xml)

    def canonicalize(xml, strip_empty):
        d = schema.decode(xml, use_defaults=True)
        # Strip extra whitespace in the schemaLocation value.
        d["@xsi:schemaLocation"] = re.sub(r"\s+", " ", d["@xsi:schemaLocation"])
        root = schema.encode(d, path=NS_OME + "OME", use_defaults=True)
        # These are the tags that appear in the example files with empty
        # content. Since our round-trip will drop empty elements, we'll need to
        # strip them from the "original" documents before comparison.
        if strip_empty:
            for tag in ("Description", "LightPath", "Map"):
                for e in root.findall(f".//{NS_OME}{tag}[.='']..."):
                    e.remove(e.find(f"{NS_OME}{tag}"))
        # ET.canonicalize can't handle an empty namespace so we need to
        # re-register the OME namespace with an actual name before calling
        # tostring.
        ElementTree.register_namespace("ome", URI_OME)
        xml_out = ElementTree.tostring(root, "unicode")
        xml_out = util.canonicalize(xml_out, strip_text=True)
        xml_out = minidom.parseString(xml_out).toprettyxml(indent="  ")
        return xml_out

    original = canonicalize(xml, True)
    ome = from_xml(xml)
    rexml = benchmark(to_xml, ome)
    assert canonicalize(rexml, False) == original


def test_to_xml_with_kwargs():
    """Ensure kwargs are passed to ElementTree"""
    ome = from_xml(Path(__file__).parent / "data" / "example.ome.xml")

    with mock.patch("xml.etree.ElementTree.tostring") as mocked_et_tostring:
        element = to_xml_element(ome)
        # Use an ElementTree.tostring kwarg and assert that it was passed through
        to_xml(element, xml_declaration=True)
        assert mocked_et_tostring.call_args.xml_declaration


@pytest.mark.parametrize("xml", xml_read, ids=true_stem)
def test_serialization(xml):
    """Test pickle serialization and reserialization."""
    if true_stem(xml) in SHOULD_RAISE_READ:
        pytest.skip("Can't pickle unreadable xml")

    ome = from_xml(xml)
    serialized = pickle.dumps(ome)
    deserialized = pickle.loads(serialized)
    assert ome == deserialized


def test_no_id():
    """Test that ids are optional, and auto-increment."""
    i = model.Instrument(id=20)
    assert i.id == "Instrument:20"
    i2 = model.Instrument()
    assert i2.id == "Instrument:21"

    # but validation still works
    with pytest.raises(ValueError):
        model.Instrument(id="nonsense")


def test_required_missing():
    """Test subclasses with non-default arguments still work."""
    with pytest.raises(ValidationError) as e:
        _ = model.BooleanAnnotation()
    assert "1 validation error for BooleanAnnotation" in str(e.value)
    assert "value\n  field required" in str(e.value)

    with pytest.raises(ValidationError) as e:
        _ = model.Label()
    assert "2 validation errors for Label" in str(e.value)
    assert "x\n  field required" in str(e.value)
    assert "y\n  field required" in str(e.value)


def test_refs():
    xml = Path(__file__).parent / "data" / "two-screens-two-plates-four-wells.ome.xml"
    ome = from_xml(xml)
    assert ome.screens[0].plate_ref[0].ref is ome.plates[0]


def test_with_ome_ns():
    xml = Path(__file__).parent / "data" / "ome_ns.ome.xml"
    ome = from_xml(xml)
    assert ome.experimenters
