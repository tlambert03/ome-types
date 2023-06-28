import pickle
import re
from pathlib import Path
from unittest import mock
from xml.dom import minidom
from xml.etree import ElementTree

import pytest
import xmlschema
from pydantic import ValidationError
from xmlschema.validators.exceptions import XMLSchemaValidationError

import ome_types
from ome_types import from_tiff, from_xml, model, to_xml

ValidationErrors = [ValidationError, XMLSchemaValidationError]
try:
    from lxml.etree import XMLSchemaValidateError

    ValidationErrors.append(XMLSchemaValidateError)
except ImportError:
    pass


SHOULD_FAIL_VALIDATION = {"invalid_xml_annotation"}
SHOULD_RAISE_READ = {"bad"}
SHOULD_FAIL_ROUNDTRIP = {
    # Order of elements in StructuredAnnotations and Union are jumbled.
    "timestampannotation-posix-only",
    "transformations-downgrade",
    "invalid_xml_annotation",
}
SHOULD_FAIL_ROUNDTRIP_LXML = {
    "folders-simple-taxonomy",
    "folders-larger-taxonomy",
}
SKIP_ROUNDTRIP = {
    # These have XMLAnnotations with extra namespaces and mixed content, which
    # the automated round-trip test code doesn't properly verify yet. So even
    # though these files do appear to round-trip correctly when checked by eye,
    # we'll play it safe and skip them until the test is fixed.
    "spim",
    "xmlannotation-body-space",
    "xmlannotation-multi-value",
    "xmlannotation-svg",
}

URI_OME = "http://www.openmicroscopy.org/Schemas/OME/2016-06"
NS_OME = "{" + URI_OME + "}"
OME_2016_06_XSD = str(Path(ome_types.__file__).parent / "ome-2016-06.xsd")


def get_schema(source: str) -> xmlschema.XMLSchema:
    schema = xmlschema.XMLSchema(OME_2016_06_XSD)
    # FIXME Hack to work around xmlschema poor support for keyrefs to
    # substitution groups
    ls_sgs = schema.maps.substitution_groups[f"{NS_OME}LightSourceGroup"]
    ls_id_maps = schema.maps.identities[f"{NS_OME}LightSourceIDKey"]
    ls_id_maps.elements = {e: None for e in ls_sgs}
    return schema


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


TESTS = Path(__file__).parent.parent
all_xml = list((TESTS / "data").glob("*.ome.xml"))
xml_roundtrip = []
for f in all_xml:
    stem = true_stem(f)
    if stem in SHOULD_RAISE_READ:
        continue
    elif stem in SHOULD_FAIL_ROUNDTRIP:
        f = mark_xfail(f)
    elif stem in SKIP_ROUNDTRIP:
        f = mark_skip(f)
    xml_roundtrip.append(f)


validate = [False]

parser = ["lxml", "xmlschema"]


@pytest.mark.parametrize("xml", all_xml, ids=true_stem)
@pytest.mark.parametrize("parser", parser)
@pytest.mark.parametrize("validate", validate)
def test_from_xml(xml, parser: str, validate: bool):
    should_raise = SHOULD_RAISE_READ.union(SHOULD_FAIL_VALIDATION if validate else [])
    if true_stem(xml) in should_raise:
        with pytest.raises(tuple(ValidationErrors)):
            assert from_xml(xml, parser=parser, validate=validate)
    else:
        assert from_xml(xml, parser=parser, validate=validate)


@pytest.mark.parametrize("parser", parser)
@pytest.mark.parametrize("validate", validate)
def test_from_tiff(validate, parser):
    """Test that OME metadata extractions from Tiff headers works."""
    _path = TESTS / "data" / "ome.tiff"
    ome = from_tiff(_path, parser=parser, validate=validate)
    assert len(ome.images) == 1
    assert ome.images[0].id == "Image:0"
    assert ome.images[0].pixels.size_x == 6
    assert ome.images[0].pixels.channels[0].samples_per_pixel == 1


@pytest.mark.parametrize("xml", xml_roundtrip, ids=true_stem)
@pytest.mark.parametrize("parser", parser)
@pytest.mark.parametrize("validate", validate)
def test_roundtrip(xml, parser, validate):
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
    ome = from_xml(xml, parser=parser, validate=validate)
    rexml = to_xml(ome)

    try:
        assert canonicalize(rexml, False) == original
    except AssertionError:
        # Special xfail catch since two files fail only with xml2dict
        if true_stem(Path(xml)) in SHOULD_FAIL_ROUNDTRIP_LXML and parser == "lxml":
            pytest.xfail(
                f"Expected failure on roundtrip using xml2dict on file: {stem}"
            )
        else:
            raise


@pytest.mark.parametrize("parser", parser)
@pytest.mark.parametrize("validate", validate)
def test_to_xml_with_kwargs(validate, parser):
    """Ensure kwargs are passed to ElementTree"""
    ome = from_xml(
        TESTS / "data" / "example.ome.xml",
        parser=parser,
        validate=validate,
    )

    with mock.patch("xml.etree.ElementTree.tostring") as mocked_et_tostring:
        element = to_xml_element(ome)
        # Use an ElementTree.tostring kwarg and assert that it was passed through
        to_xml(element, xml_declaration=True)
        assert mocked_et_tostring.call_args.xml_declaration


@pytest.mark.parametrize("xml", all_xml, ids=true_stem)
@pytest.mark.parametrize("parser", parser)
@pytest.mark.parametrize("validate", validate)
def test_serialization(xml, validate, parser):
    """Test pickle serialization and reserialization."""
    if true_stem(xml) in SHOULD_RAISE_READ:
        pytest.skip("Can't pickle unreadable xml")
    if validate and true_stem(xml) in SHOULD_FAIL_VALIDATION:
        pytest.skip("Can't pickle invalid xml with validate=True")

    ome = from_xml(xml, parser=parser, validate=validate)
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


@pytest.mark.parametrize("parser", parser)
@pytest.mark.parametrize("validate", validate)
def test_refs(validate, parser) -> None:
    xml = TESTS / "data" / "two-screens-two-plates-four-wells.ome.xml"
    ome = from_xml(xml, parser=parser, validate=validate)
    assert ome.screens[0].plate_ref[0].ref is ome.plates[0]


@pytest.mark.parametrize("validate", validate)
@pytest.mark.parametrize("parser", parser)
def test_with_ome_ns(validate, parser) -> None:
    xml = TESTS / "data" / "ome_ns.ome.xml"
    ome = from_xml(xml, parser=parser, validate=validate)
    assert ome.experimenters
