import importlib
import sys
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

import ome_autogen.main
from ome_autogen import _generator
from ome_types._mixins import _base_type


def test_autogen(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Test that autogen works without raising an exception.

    and that mypy has no issues with it.
    """
    ome_autogen.main.build_model(output_dir=tmp_path, do_formatting=True, do_mypy=True)

    monkeypatch.delitem(sys.modules, "ome_types")
    monkeypatch.delitem(sys.modules, "ome_types.model")
    monkeypatch.delitem(sys.modules, "ome_types.model.ome_2016_06")
    monkeypatch.syspath_prepend(str(tmp_path))
    mod = importlib.import_module("ome_types.model.ome_2016_06")
    assert mod.__file__ and mod.__file__.startswith(str(tmp_path))
    assert mod.Channel(color="blue")


def test_autosequence_name() -> None:
    """These should match, but shouldn't be imported from each other."""
    assert _generator.AUTO_SEQUENCE == _base_type.AUTO_SEQUENCE
