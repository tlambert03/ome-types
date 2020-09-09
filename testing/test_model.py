from pathlib import Path

import pytest
from xmlschema.validators.exceptions import XMLSchemaValidationError

from ome_types import from_xml, model

SHOULD_FAIL = {
    # Some timestamps have negative years which datetime doesn't support.
    "timestampannotation",
    "mapannotation",
}
SHOULD_RAISE = {"bad"}


def mark_xfail(fname):
    return pytest.param(
        fname,
        marks=pytest.mark.xfail(
            strict=True, reason="Unexpected success. You fixed it!"
        ),
    )


def true_stem(p):
    return p.name.partition(".")[0]


params = [
    mark_xfail(f) if true_stem(f) in SHOULD_FAIL else f
    for f in Path(__file__).parent.glob("data/*.ome.xml")
]


@pytest.mark.parametrize("xml", params, ids=true_stem)
def test_convert_schema(xml):

    if true_stem(xml) in SHOULD_RAISE:
        with pytest.raises(XMLSchemaValidationError):
            assert from_xml(xml)
    else:
        assert from_xml(xml)


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
