from __future__ import annotations

from dataclasses import MISSING, field
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from pydantic import BaseModel, version

if TYPE_CHECKING:
    from typing import Iterator

    from pydantic import Field


__all__ = ["Field"]
PYDANTIC2 = version.VERSION.startswith("2")
M = TypeVar("M", bound=BaseModel)
C = TypeVar("C", bound=Callable[..., Any])


if PYDANTIC2:
    from pydantic.fields import Field as _Field
    from pydantic.fields import FieldInfo
    from pydantic_core import PydanticUndefined as Undefined

    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore
        if "metadata" in kwargs:
            kwargs["json_schema_extra"] = kwargs.pop("metadata")
        if "regex" in kwargs:
            kwargs["pattern"] = kwargs.pop("regex")
        if "min_items" in kwargs:
            kwargs["min_length"] = kwargs.pop("min_items")
        return _Field(*args, **kwargs)  # type: ignore

    def _get_metadata(pydantic_field: FieldInfo) -> dict[str, Any]:
        return (
            pydantic_field.json_schema_extra
            if isinstance(pydantic_field.json_schema_extra, dict)
            else {}
        )

else:
    from pydantic.fields import Field as _Field
    from pydantic.fields import Undefined as Undefined  # type: ignore

    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore
        if "metadata" in kwargs:
            kwargs["json_schema_extra"] = kwargs.pop("metadata")
        return _Field(*args, **kwargs)  # type: ignore

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

    dataclass_field = field(  # type: ignore
        default=default,
        default_factory=default_factory,
        # init=True,
        # hash=None,
        # compare=True,
        metadata=metadata,
        # kw_only=MISSING,
    )
    dataclass_field.name = name
    # dataclass_field.type = pydantic_field.type_
    return dataclass_field


def dataclass_fields(obj: type[M]) -> Iterator[Any]:
    for name, f in obj.model_fields.items():
        yield _pydantic_field_to_dataclass_field(name, f)
