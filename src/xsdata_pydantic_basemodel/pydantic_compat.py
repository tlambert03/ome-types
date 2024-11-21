from __future__ import annotations

import dataclasses as dc
import warnings
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from pydantic_compat import PYDANTIC2, Field

__all__ = ["Field", "PYDANTIC2"]

if TYPE_CHECKING:
    from pydantic import BaseModel

    M = TypeVar("M", bound=BaseModel)
    C = TypeVar("C", bound=Callable[..., Any])


if PYDANTIC2:
    from pydantic.fields import FieldInfo
    from pydantic_core import PydanticUndefined as Undefined

    def _get_metadata(pydantic_field: FieldInfo) -> dict[str, Any]:
        meta = (
            pydantic_field.json_schema_extra
            if isinstance(pydantic_field.json_schema_extra, dict)
            else {}
        )
        # if a "metadata" key exists... use it.
        # After pydantic-compat 0.2, this is where it will be.
        if "metadata" in meta:
            meta = meta["metadata"]  # type: ignore
        return meta

else:
    from pydantic.fields import Undefined as Undefined  # type: ignore

    def _get_metadata(pydantic_field) -> dict:  # type: ignore
        extra = pydantic_field.field_info.extra
        if "json_schema_extra" in extra:
            return extra["json_schema_extra"]
        return extra.get("metadata", {})


def _get_defaults(pydantic_field: FieldInfo) -> tuple[Any, Any]:
    if pydantic_field.default_factory is not None:
        default_factory: Any = pydantic_field.default_factory
        default = dc.MISSING
    else:
        default_factory = dc.MISSING
        default = (
            dc.MISSING
            if pydantic_field.default in (Undefined, Ellipsis)
            else pydantic_field.default
        )
    return default_factory, default


def _pydantic_field_to_dataclass_field(
    name: str, pydantic_field: FieldInfo
) -> dc.Field:
    default_factory, default = _get_defaults(pydantic_field)

    metadata = _get_metadata(pydantic_field).copy()

    # HACK
    # see https://github.com/tlambert03/ome-types/pull/235 for description of problem
    # This is a hack to get around the fact that xsdata requires Element choices
    # to be added to the Field metadata as `choices: List[dict]` ... but pydantic
    # requires that everything in a Field be hashable (if you want to cast the model
    # to a JSON schema), and `dict` is not hashable. So here, when we're converting
    # a pydantic Field to a dataclass Field for xsdata to consume, we cast all items
    # in the `choices` list to `dict` (which is hashable).
    # Then, in our source code, we declare choices as tuple[tuple[str, str], ...]
    # which IS hashable.
    if "choices" in metadata:
        choices = []
        for choice in metadata["choices"]:
            choice = dict(choice)
            # we also, unfortunately, need to convert the "type" field from a
            # class name to a class object
            if "type" in choice and isinstance(choice["type"], str):
                try:
                    from ome_types import model

                    choice["type"] = getattr(model, choice["type"])
                except AttributeError:
                    warnings.warn(
                        f"Could not find {choice['type']} in ome_types.model",
                        stacklevel=2,
                    )

            choices.append(choice)
        metadata["choices"] = choices

    dataclass_field = dc.field(  # type: ignore
        default=default, default_factory=default_factory, metadata=metadata
    )
    dataclass_field.name = name
    return dataclass_field


@lru_cache(maxsize=None)
def dataclass_fields(obj: type[M]) -> tuple[dc.Field, ...]:
    """Return a tuple of dataclass fields for the given pydantic model class."""
    return tuple(
        _pydantic_field_to_dataclass_field(name, f)
        for name, f in obj.model_fields.items()  # type: ignore
    )
