import importlib
import os
import sys
from glob import glob
from xmlschema.validators.exceptions import XMLSchemaValidationError
import pytest

from omelite.autogen import convert_schema
from omelite import from_xml

this_dir = os.path.dirname(__file__)


@pytest.fixture(scope="session")
def model(tmpdir_factory):
    target = tmpdir_factory.mktemp("test_model")
    url = os.path.join(this_dir, "ome.xsd")
    convert_schema(url, target)
    sys.path.insert(0, os.path.dirname(str(target)))
    model_name = os.path.basename(str(target))
    model_module = importlib.import_module(model_name)
    return model_module


@pytest.mark.parametrize(
    "xml", glob(os.path.join(this_dir, "*.xml")), ids=lambda x: os.path.basename(x)
)
def test_convert_schema(model, xml):
    if "bad.xml" in xml:
        with pytest.raises(XMLSchemaValidationError):
            assert from_xml(xml, model.OME)
    else:
        assert from_xml(xml, model.OME)
