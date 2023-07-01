from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import pytest

from ome_types import (
    validate_xml,  # noqa: F401 ... just to make sure it's importable
    validation,
)

if TYPE_CHECKING:
    from pathlib import Path

VALIDATORS: dict[str, Callable] = {
    "lxml": validation.validate_xml_with_lxml,
    "xmlschema": validation.validate_xml_with_xmlschema,
}


@pytest.mark.parametrize("backend", ["lxml", "xmlschema"])
def test_validation_good(valid_xml: Path, backend: str) -> None:
    VALIDATORS[backend](valid_xml)


@pytest.mark.parametrize("backend", ["lxml", "xmlschema"])
def test_validation_raises(invalid_xml: Path, backend: str) -> None:
    with pytest.raises(validation.ValidationError):
        VALIDATORS[backend](invalid_xml)