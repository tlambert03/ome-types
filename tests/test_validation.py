from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Callable

import pytest

from ome_types import validate_xml, validation

if TYPE_CHECKING:
    from pathlib import Path

VALIDATORS: dict[str, Callable] = {}
with contextlib.suppress(ImportError):
    import lxml  # noqa: F401

    VALIDATORS["lxml"] = validation.validate_xml_with_lxml

with contextlib.suppress(ImportError):
    import xmlschema  # noqa: F401

    VALIDATORS["xmlschema"] = validation.validate_xml_with_xmlschema


@pytest.mark.parametrize("backend", VALIDATORS)
def test_validation_good(valid_xml: Path, backend: str) -> None:
    VALIDATORS[backend](valid_xml)


def test_validation_anybackend(single_xml: Path) -> None:
    if VALIDATORS:
        validate_xml(single_xml)
    else:
        with pytest.raises(ImportError):
            validate_xml(single_xml)


@pytest.mark.parametrize("backend", VALIDATORS)
def test_validation_raises(invalid_xml: Path, backend: str) -> None:
    with pytest.raises(validation.ValidationError):
        VALIDATORS[backend](invalid_xml)
