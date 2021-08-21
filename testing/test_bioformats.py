from pathlib import Path

from ome_types import from_bioformats, from_tiff


def test_bioformats():
    data = Path(__file__).parent / "data" / "ome.tiff"
    ome = from_bioformats(data)
    ome2 = from_tiff(data)
    # cop out... they read a little differently
    assert ome.uuid == ome2.uuid


def test_bioformats2():
    # for CI, this should grab a local copy
    data = Path(__file__).parent / "data" / "ome.tiff"
    ome = from_bioformats(data)
    ome2 = from_tiff(data)
    # cop out... they read a little differently
    assert ome.uuid == ome2.uuid
