from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from some_types import SOME, from_tiff, from_xml, to_dict, to_xml

if all(x not in {"--codspeed", "tests/test_codspeed.py"} for x in sys.argv):
    pytest.skip("use --codspeed to run benchmarks", allow_module_level=True)

if TYPE_CHECKING:
    from pytest_codspeed.plugin import BenchmarkFixture


DATA = Path(__file__).parent / "data"
TIFF = DATA / "some.tiff"  # 1KB
SMALL = DATA / "multi-channel.some.xml"  # 1KB
MED = DATA / "two-screens-two-plates-four-wells.some.xml"  # 16KB
LARGE = DATA / "OverViewScan2-aics.some.xml"  # 972KB
XML = [SMALL, MED, LARGE]


@pytest.mark.benchmark
@pytest.mark.parametrize("file", XML, ids=["small", "med", "large"])
def test_time_from_xml(file: Path) -> None:
    _ = from_xml(file)


@pytest.mark.parametrize("file", XML, ids=["small", "med", "large"])
def test_time_to_xml(file: Path, benchmark: BenchmarkFixture) -> None:
    some = from_xml(file)
    benchmark(lambda: to_xml(some))


@pytest.mark.benchmark
def test_time_from_tiff() -> None:
    _ = from_tiff(TIFF)


@pytest.mark.parametrize("file", [SMALL, MED], ids=["small", "med"])
def test_time_from_xml_to_dict(file: Path) -> None:
    _ = to_dict(file)


@pytest.mark.parametrize("file", [SMALL, MED], ids=["small", "med"])
def test_time_from_dict_to_some(file: Path, benchmark: BenchmarkFixture) -> None:
    d = to_dict(file)
    benchmark(lambda: SOME(**d))
