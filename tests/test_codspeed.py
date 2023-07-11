from __future__ import annotations

import sys
from pathlib import Path

import pytest

from ome_types import from_tiff, from_xml, to_xml

if all(x not in {"--codspeed", "tests/test_codspeed.py"} for x in sys.argv):
    pytest.skip("use --codspeed to run benchmarks", allow_module_level=True)

DATA = Path(__file__).parent / "data"
TIFF = DATA / "ome.tiff"  # 1KB
SMALL = DATA / "multi-channel.ome.xml"  # 1KB
MED = DATA / "two-screens-two-plates-four-wells.ome.xml"  # 16KB
LARGE = DATA / "OverViewScan2-aics.ome.xml"  # 972KB
XML = [SMALL, MED, LARGE]


@pytest.mark.benchmark
@pytest.mark.parametrize("file", XML, ids=["small", "med", "large"])
def test_time_from_xml(file: Path) -> None:
    _ = from_xml(file)


@pytest.mark.parametrize("file", XML, ids=["small", "med", "large"])
def test_time_to_xml(file: Path, benchmark) -> None:
    ome = from_xml(file)
    benchmark(lambda: to_xml(ome))


@pytest.mark.benchmark
def test_time_from_tiff() -> None:
    _ = from_tiff(TIFF)
