from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, DefaultDict

import pytest

from ome_types import model
from ome_types._mixins import _base_type

if TYPE_CHECKING:
    from collections import defaultdict

DATA = Path(__file__).parent / "data"
ALL_XML = set(DATA.glob("*.ome.xml"))
INVALID = {DATA / "invalid_xml_annotation.ome.xml", DATA / "bad.ome.xml"}


def _true_stem(p: Path) -> str:
    return p.name.partition(".")[0]


@pytest.fixture(params=sorted(ALL_XML), ids=_true_stem)
def any_xml(request: pytest.FixtureRequest) -> Path:
    return request.param


@pytest.fixture(params=sorted(ALL_XML - INVALID), ids=_true_stem)
def valid_xml(request: pytest.FixtureRequest) -> Path:
    return request.param


@pytest.fixture(params=INVALID, ids=_true_stem)
def invalid_xml(request: pytest.FixtureRequest) -> Path:
    return request.param


@pytest.fixture
def single_xml() -> Path:
    return DATA / "example.ome.xml"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--ome-watch",
        action="store_true",
        default=False,
        help="Monitor instantiation of all OME objects.",
    )


USED_CLASS_KWARGS: defaultdict[str, set[str]] = DefaultDict(set)


@pytest.fixture(autouse=True, scope="session")
def _monitor(request: pytest.FixtureRequest) -> None:
    """Monitor instantiation of all OME objects.

    This is another form of coverage... to see what fields are actually being tested
    by our data
    """
    if not request.config.getoption("--ome-watch"):
        return

    original = _base_type.OMEType.__init__

    def patched(__pydantic_self__, **kwargs: Any) -> None:
        original(__pydantic_self__, **kwargs)
        USED_CLASS_KWARGS[__pydantic_self__.__class__.__name__].update(kwargs)

    _base_type.OMEType.__init__ = patched


def print_unused_kwargs() -> None:
    """Print a table of unused kwargs for each class."""
    from rich.console import Console
    from rich.table import Table

    table = Table(title="Class usage summary", border_style="cyan", expand=True)
    table.add_column("Class", style="cyan")
    table.add_column("Unused fields", style="red", max_width=50)
    table.add_column("Percent Used", style="Green")

    rows: list[tuple[str, str, float]] = []
    total_fields = 0
    total_used = 0
    for cls_name in dir(model):
        # loop over all classes in the model
        cls = getattr(model, cls_name, None)
        if not isinstance(cls, type):
            continue

        # get a list of all fields (ignore refs)
        all_fields: set[str] = set(getattr(cls, "__fields__", {}))
        all_fields = {f for f in all_fields if not f.rstrip("s").endswith("ref")}
        for base_cls in cls.__bases__:
            all_fields -= set(getattr(base_cls, "__fields__", {}))
        if not all_fields:
            continue

        # determine how many have been used
        used = USED_CLASS_KWARGS[cls_name]
        unused_fields = all_fields - used
        total_fields += len(all_fields)
        total_used += len(all_fields) - len(unused_fields)
        percent_used = 100 * (1 - len(unused_fields) / len(all_fields))
        if percent_used < 100:
            rows.append((cls_name, ", ".join(unused_fields), percent_used))

    # sort by percent used
    for row in sorted(rows, key=lambda r: r[2]):
        name, unused, percent = row
        table.add_row(name, unused, f"{percent:.1f}%")
    # add total
    table.add_row(
        "[bold yellow]TOTAL[/bold yellow]",
        "",
        f"{100 * total_used / total_fields:.1f}%",
    )
    # print
    Console().print(table)


@pytest.hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
    if not config.getoption("--ome-watch"):
        return

    from _pytest.terminal import TerminalReporter

    class CustomTerminalReporter(TerminalReporter):  # type: ignore
        def summary_stats(self) -> None:
            super().summary_stats()
            print_unused_kwargs()

    # Get the standard terminal reporter plugin and replace it with our
    standard_reporter = config.pluginmanager.getplugin("terminalreporter")
    custom_reporter = CustomTerminalReporter(config, sys.stdout)
    config.pluginmanager.unregister(standard_reporter)
    config.pluginmanager.register(custom_reporter, "terminalreporter")
