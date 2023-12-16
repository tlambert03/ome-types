from __future__ import annotations

from dataclasses import MISSING, field
from typing import TYPE_CHECKING, Any, Callable, Iterator, TypeVar

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
        return (
            pydantic_field.json_schema_extra
            if isinstance(pydantic_field.json_schema_extra, dict)
            else {}
        )

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
        default = MISSING
    else:
        default_factory = MISSING
        default = (
            MISSING
            if pydantic_field.default in (Undefined, Ellipsis)
            else pydantic_field.default
        )
    return default_factory, default


def _pydantic_field_to_dataclass_field(name: str, pydantic_field: FieldInfo) -> Any:
    default_factory, default = _get_defaults(pydantic_field)

    metadata = _get_metadata(pydantic_field)

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
        metadata["choices"] = [dict(choice) for choice in metadata["choices"]]

    dataclass_field = field(  # type: ignore
        default=default, default_factory=default_factory, metadata=metadata
    )
    dataclass_field.name = name
    return dataclass_field


def dataclass_fields(obj: type[M]) -> Iterator[Any]:
    for name, f in obj.model_fields.items():
        yield _pydantic_field_to_dataclass_field(name, f)
