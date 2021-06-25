from pathlib import Path

import pytest

nplg = pytest.importorskip("ome_types._napari_plugin")

DATA = Path(__file__).parent / "data"


@pytest.mark.parametrize("fname", DATA.iterdir(), ids=lambda x: x.stem)
def test_widget(fname, qtbot):
    if fname.stem in ("bad.ome", "timestampannotation.ome"):
        pytest.xfail()
    nplg.OMETree(str(fname))
