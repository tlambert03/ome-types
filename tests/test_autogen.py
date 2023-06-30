import importlib
import sys
from pathlib import Path

import pytest

ome_autogen = pytest.importorskip("_ome_autogen")
XSD = Path(__file__).parent.parent.parent / "src" / "ome_types" / "ome-2016-06.xsd"


def test_autogen(tmp_path_factory):
    """Test that autogen works without raising an exception.

    This does *not* actually test the resulting model.
    """
    target_dir = tmp_path_factory.mktemp("_ome_types_test_model")
    ome_autogen.convert_schema(url=XSD, target_dir=target_dir)
    sys.path.insert(0, str(target_dir.parent))
    assert importlib.import_module(target_dir.name)
    sys.path.pop(0)
