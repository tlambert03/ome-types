import importlib
import os
import sys
from glob import glob

import pytest
from xmlschema.validators.exceptions import XMLSchemaValidationError

from ome_autogen import convert_schema
from ome_types import from_xml
from pathlib import Path


TESTING_DIR = Path(__file__).parent


@pytest.fixture(scope="session")
def model(tmp_path_factory):
    target_dir = tmp_path_factory.mktemp("test_model")
    xsd = TESTING_DIR / "ome-2016-06.xsd"
    convert_schema(url=xsd, target_dir=target_dir)
    sys.path.insert(0, str(target_dir.parent))
    return importlib.import_module(target_dir.name)


SHOULD_PASS = {"example.ome", "small.ome"}
SHOULD_RAISE = {"bad.ome"}


def mark_xfail(fname):
    return pytest.param(
        fname,
        marks=pytest.mark.xfail(
            strict=True, reason="Unexpected success. You fixed it!"
        ),
    )


params = [
    f if f.stem in SHOULD_PASS.union(SHOULD_RAISE) else mark_xfail(f)
    for f in TESTING_DIR.glob("data/*.xml")
]


@pytest.mark.parametrize("xml", params, ids=lambda x: x.stem)
def test_convert_schema(model, xml):
    if xml.stem in SHOULD_RAISE:
        with pytest.raises(XMLSchemaValidationError):
            assert from_xml(xml, model.OME)
    else:
        assert from_xml(xml, model.OME)
