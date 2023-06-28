import pickle
from pathlib import Path

import pydantic
import pytest

from ome_types import OME, from_tiff, from_xml, to_xml
from ome_types.model import ome_2016_06 as model

DATA = Path(__file__).parent.parent / "data"
ALL_XML = set(DATA.glob("*.ome.xml"))
INVALID = {DATA / "invalid_xml_annotation.ome.xml", DATA / "bad.ome.xml"}


def _true_stem(p: Path) -> str:
    return p.name.partition(".")[0]


@pytest.fixture(params=sorted(ALL_XML), ids=_true_stem)
def any_xml(request: pytest.FixtureRequest) -> Path:
    return request.param


@pytest.fixture(params=sorted(ALL_XML - INVALID), ids=_true_stem)
def valid_xml(request: pytest.FixtureRequest) -> Path:
    return request.param


@pytest.fixture(params=INVALID, ids=_true_stem)
def invalid_xml(request: pytest.FixtureRequest) -> Path:
    return request.param


@pytest.mark.filterwarnings("ignore::ResourceWarning")  # FIXME
def test_from_xml(any_xml: Path) -> None:
    if any_xml in INVALID:
        with pytest.raises(pydantic.ValidationError):
            from_xml(any_xml)
    else:
        assert isinstance(from_xml(any_xml), OME)


def test_from_tiff() -> None:
    """Test that OME metadata extractions from Tiff headers works."""
    ome = from_tiff(DATA / "ome.tiff")
    assert len(ome.images) == 1
    assert ome.images[0].id == "Image:0"
    assert ome.images[0].pixels.size_x == 6
    assert ome.images[0].pixels.channels[0].samples_per_pixel == 1


@pytest.mark.filterwarnings("ignore::ResourceWarning")  # FIXME
def test_serialization(valid_xml: Path) -> None:
    """Test pickle serialization and reserialization."""
    ome = from_xml(valid_xml)
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


def test_required_missing() -> None:
    """Test subclasses with non-default arguments still work."""
    with pytest.raises(pydantic.ValidationError, match="value\n  field required"):
        model.BooleanAnnotation()

    with pytest.raises(pydantic.ValidationError, match="x\n  field required"):
        model.Label()


def test_refs() -> None:
    xml = DATA / "two-screens-two-plates-four-wells.ome.xml"
    ome = from_xml(xml)
    assert ome.screens[0].plate_refs[0].ref is ome.plates[0]


def test_with_ome_ns() -> None:
    assert from_xml(DATA / "ome_ns.ome.xml").experimenters


def test_roundtrip_inverse(valid_xml, tmp_path: Path):
    """both variants have been touched by the model, here..."""
    ome1 = from_xml(valid_xml)

    xml = to_xml(ome1)
    out = tmp_path / "test.xml"
    out.write_bytes(xml.encode())
    ome2 = from_xml(out)

    assert ome1 == ome2


# def test_roundtrip():
#     """Ensure we can losslessly round-trip XML through the model and back."""
#     valid_xml = Path(DATA / "example.ome.xml")
#     raw_bytes = valid_xml.read_bytes()
#     node1 = etree.fromstring(raw_bytes)
#     canonical_input = etree.tostring(node1, method="c14n2")

#     ome = from_xml(valid_xml)
#     rexml = to_xml(ome)

#     node2 = etree.fromstring(rexml.encode())
#     canonical_output = etree.tostring(node2, method="c14n2")

#     assert canonical_input == canonical_output
# try:
#     assert canonicalize(rexml, False) == original
# except AssertionError:
#     # Special xfail catch since two files fail only with xml2dict
#     if true_stem(Path(xml)) in SHOULD_FAIL_ROUNDTRIP_LXML and parser == "lxml":
#         pytest.xfail(
#             f"Expected failure on roundtrip using xml2dict on file: {stem}"
#         )
#     else:
#         raise
