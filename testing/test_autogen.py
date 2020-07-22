import importlib
import sys
from pathlib import Path

import pytest
from xmlschema.validators.exceptions import XMLSchemaValidationError

TESTING_DIR = Path(__file__).parent
SRC = TESTING_DIR.parent / "src" / "ome_types"
SRC_MODEL = SRC / "model"


@pytest.fixture(scope="session")
def model(tmp_path_factory, request):
    if request.config.getoption("--nogen"):
        if not SRC_MODEL.exists():
            raise RuntimeError(
                f"Please generate local {SRC_MODEL} before using --nogen"
            )
        sys.path.insert(0, str(SRC_MODEL))
        return importlib.import_module(SRC_MODEL.name)
    from ome_autogen import convert_schema

    target_dir = tmp_path_factory.mktemp("test_model")
    xsd = SRC / "ome-2016-06.xsd"
    convert_schema(url=xsd, target_dir=target_dir)
    sys.path.insert(0, str(target_dir.parent))
    return importlib.import_module(target_dir.name)


SHOULD_FAIL = {
    "commentannotation",
    "mapannotation",
    "spim",
    "tagannotation",
    "timestampannotation",
    "timestampannotation-posix-only",
    "transformations-downgrade",
    "transformations-upgrade",
    "xmlannotation-body-space",
    "xmlannotation-multi-value",
    "xmlannotation-svg",
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
    for f in TESTING_DIR.glob("data/*.ome.xml")
]


@pytest.mark.parametrize("xml", params, ids=true_stem)
def test_convert_schema(model, xml):
    from ome_types import from_xml

    if true_stem(xml) in SHOULD_RAISE:
        with pytest.raises(XMLSchemaValidationError):
            assert from_xml(xml, model.OME)
    else:
        assert from_xml(xml, model.OME)
