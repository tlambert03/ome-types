import importlib
import os
import sys
from importlib.util import find_spec
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from ome_types._mixins import _base_type


@pytest.fixture
def imports_autogen(monkeypatch: MonkeyPatch) -> None:
    """This fixture adds the src folder to sys.path so we can import ome_autogen.

    The goal here is to be able to run `pip install .[test,dev]` on CI, NOT in editable
    mode, but still be able to test autogen without requiring it to be included in the
    wheel.
    """
    if not find_spec("ome_autogen"):
        SRC = Path(__file__).parent.parent / "src"
        assert (SRC / "ome_autogen").is_dir()
        monkeypatch.syspath_prepend(str(SRC))


@pytest.mark.skipif(sys.version_info < (3, 8), reason="docs fail on python3.7")
@pytest.mark.skipif(not os.getenv("CI"), reason="slow")
@pytest.mark.usefixtures("imports_autogen")
def test_autogen(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Test that autogen works without raising an exception.

    and that mypy has no issues with it.
    """
    import ome_autogen.main

    ome_autogen.main.build_model(output_dir=tmp_path, do_formatting=True, do_mypy=True)

    monkeypatch.delitem(sys.modules, "ome_types")
    monkeypatch.delitem(sys.modules, "ome_types._autogenerated")
    monkeypatch.delitem(sys.modules, "ome_types._autogenerated.ome_2016_06")
    monkeypatch.syspath_prepend(str(tmp_path))
    mod = importlib.import_module("ome_types._autogenerated.ome_2016_06")
    assert mod.__file__
    assert mod.__file__.startswith(str(tmp_path))
    assert mod.Channel(color="blue")


@pytest.mark.usefixtures("imports_autogen")
def test_autosequence_name() -> None:
    """These should match, but shouldn't be imported from each other."""
    from ome_autogen import _generator

    assert _generator.AUTO_SEQUENCE == _base_type.AUTO_SEQUENCE
