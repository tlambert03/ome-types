from pathlib import Path

import pytest

try:
    from ome_types import widget
except ImportError:
    pytest.skip("ome_types not installed", allow_module_level=True)


def test_widget(valid_xml: Path, qtbot):
    widget.OMETree(str(valid_xml))
