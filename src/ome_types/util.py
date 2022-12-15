from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

from . import model
from ._base_type import OMEType
from .model.reference import Reference

if TYPE_CHECKING:
    from .model.simple_types import LSID


def cast_number(qnum: str) -> str | int | float:
    """Attempt to cast a number from a string.

    This function attempts to cast a string to a number. It will first try to parse an
    int, then a float, and finally returns a string if both fail.
    """
    try:
        return int(qnum)
    except ValueError:
        try:
            return float(qnum)
        except ValueError:
            return qnum


def collect_references(value: Any) -> list[Reference]:
    """Return a list of all References contained in value.

    Recursively walks all dataclass fields and iterates over lists. The base
    case is when value is either a Reference object, or an uninteresting type
    that we don't need to inspect further.

    """
    references: list[Reference] = []
    if isinstance(value, Reference):
        references.append(value)
    elif isinstance(value, list):
        for v in value:
            references.extend(collect_references(v))
    elif isinstance(value, OMEType):
        for f in value.__fields__:
            references.extend(collect_references(getattr(value, f)))
    # Do nothing for uninteresting types
    return references


def collect_ids(value: Any) -> dict[LSID, OMEType]:
    """Return a map of all model objects contained in value, keyed by id.

    Recursively walks all dataclass fields and iterates over lists. The base
    case is when value is neither a dataclass nor a list.
    """
    ids: dict[LSID, OMEType] = {}
    if isinstance(value, list):
        for v in value:
            ids.update(collect_ids(v))
    elif isinstance(value, OMEType):
        for f in value.__fields__:
            if f == "id" and not isinstance(value, Reference):
                # We don't need to recurse on the id string, so just record it
                # and move on.
                ids[value.id] = value  # type: ignore
            else:
                ids.update(collect_ids(getattr(value, f)))
    # Do nothing for uninteresting types.
    return ids


CAMEL_REGEX = re.compile(r"(?<!^)(?=[A-Z])")


@lru_cache()
def camel_to_snake(name: str) -> str:
    """Return a snake_case version of a camelCase string."""
    return model._camel_to_snake.get(name, CAMEL_REGEX.sub("_", name).lower())


@lru_cache()
def norm_key(key: str) -> str:
    """Return a normalized key."""
    return key.split("}")[-1]


def _get_plural(key: str, tag: str) -> str:
    return model._singular_to_plural.get((norm_key(tag), key), key)


def _ensure_xml_bytes(path_or_str: Path | str | bytes) -> bytes:
    """Ensure that `path_or_str` is bytes.  Read from disk if it's an existing file."""
    if isinstance(path_or_str, Path):
        return path_or_str.read_bytes()
    if isinstance(path_or_str, str):
        # FIXME: deal with magic number 10.  I think it's to avoid Path.exists
        # failure on a full string
        if "xml" not in path_or_str[:10] and Path(path_or_str).exists():
            return Path(path_or_str).read_bytes()
        else:
            return path_or_str.encode()
    if isinstance(path_or_str, bytes):
        return path_or_str
    raise TypeError("path_or_str must be one of [Path, str, bytes].  I")
