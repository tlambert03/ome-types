import re
from pathlib import Path
from xml.dom import minidom
from xml.etree import ElementTree

import pytest
from xmlschema.validators.exceptions import XMLSchemaValidationError

from ome_types import from_xml, model, to_xml
from ome_types.schema import NS_OME, URI_OME, get_schema

SHOULD_FAIL_READ = {
    # Some timestamps have negative years which datetime doesn't support.
    "timestampannotation",
}
SHOULD_RAISE_READ = {"bad"}
SHOULD_FAIL_ROUNDTRIP = {
    "spim",
    "timestampannotation",
    "timestampannotation-posix-only",
    "transformations-downgrade",
    "transformations-upgrade",
    "xmlannotation-body-space",
    "xmlannotation-multi-value",
    "xmlannotation-svg",
}


def mark_xfail(fname):
    return pytest.param(
        fname,
        marks=pytest.mark.xfail(
            strict=True, reason="Unexpected success. You fixed it!"
        ),
    )


def true_stem(p):
    return p.name.partition(".")[0]


all_xml = list((Path(__file__).parent / "data").glob("*.ome.xml"))
xml_read = [mark_xfail(f) if true_stem(f) in SHOULD_FAIL_READ else f for f in all_xml]
xml_roundtrip = [
    mark_xfail(f) if true_stem(f) in SHOULD_FAIL_ROUNDTRIP else f
    for f in all_xml
    if true_stem(f) not in SHOULD_FAIL_READ | SHOULD_RAISE_READ
]


@pytest.mark.parametrize("xml", xml_read, ids=true_stem)
def test_read(xml):

    if true_stem(xml) in SHOULD_RAISE_READ:
        with pytest.raises(XMLSchemaValidationError):
            assert from_xml(xml)
    else:
        assert from_xml(xml)


@pytest.mark.parametrize("xml", xml_roundtrip, ids=true_stem)
def test_roundtrip(xml):
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
        xml_out = ElementTree.canonicalize(xml_out, strip_text=True)
        xml_out = minidom.parseString(xml_out).toprettyxml(indent="  ")
        return xml_out

    original = canonicalize(xml, True)
    ours = canonicalize(to_xml(from_xml(xml)), False)
    assert ours == original


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
    with pytest.raises(TypeError) as e:
        _ = model.BooleanAnnotation()
    assert "missing 1 required argument: ['value']" in str(e)

    with pytest.raises(TypeError) as e:
        _ = model.Label()
    assert "missing 2 required arguments: ['x', 'y']" in str(e)
