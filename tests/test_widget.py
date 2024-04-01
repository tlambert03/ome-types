from pathlib import Path

import pytest

try:
    from some_types import widget
except ImportError:
    pytest.skip("some_types not installed", allow_module_level=True)


def test_widget(valid_xml: Path, qtbot):
    widget.SOMETree(str(valid_xml))
