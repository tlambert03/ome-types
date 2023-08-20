from __future__ import annotations

from dataclasses import MISSING, field
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from pydantic import BaseModel, version

if TYPE_CHECKING:
    from typing import Iterator, Literal

    from pydantic import Field


__all__ = ["Field"]
PYDANTIC2 = version.VERSION.startswith("2")
M = TypeVar("M", bound=BaseModel)
C = TypeVar("C", bound=Callable[..., Any])


# no-op for v1, put first for typing.
def model_validator(*, mode: Literal["wrap", "before", "after"]) -> Callable[[C], C]:
    def decorator(func: C) -> C:
        return func

    return decorator


if PYDANTIC2:
    from pydantic import field_validator
    from pydantic import model_validator as model_validator  # type: ignore # noqa
    from pydantic.fields import Field as _Field
    from pydantic.fields import FieldInfo
    from pydantic_core import PydanticUndefined as Undefined

    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore # noqa
        if "metadata" in kwargs:
            kwargs["json_schema_extra"] = kwargs.pop("metadata")
        if "regex" in kwargs:
            kwargs["pattern"] = kwargs.pop("regex")
        if "min_items" in kwargs:
            kwargs["min_length"] = kwargs.pop("min_items")
        return _Field(*args, **kwargs)  # type: ignore

    def validator(*args: Any, **kwargs: Any) -> Callable[[Callable], Callable]:
        return field_validator(*args, **kwargs)

    def update_forward_refs(cls: type[M]) -> None:
        try:
            cls.model_rebuild()
        except AttributeError:
            pass

    def iter_fields(obj: type[M]) -> Iterator[tuple[str, FieldInfo]]:
        yield from obj.model_fields.items()

    def _get_metadata(pydantic_field: FieldInfo) -> dict[str, Any]:
        return (
            pydantic_field.json_schema_extra
            if isinstance(pydantic_field.json_schema_extra, dict)
            else {}
        )

    def model_config(**kwargs: Any) -> dict | type:
        return kwargs

    def fields_set(obj: BaseModel) -> set[str]:
        return obj.model_fields_set

else:
    from pydantic.fields import Field as _Field
    from pydantic.fields import ModelField  # type: ignore
    from pydantic.fields import Undefined as Undefined  # type: ignore

    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore
        if "metadata" in kwargs:
            kwargs["json_schema_extra"] = kwargs.pop("metadata")
        return _Field(*args, **kwargs)  # type: ignore

    def update_forward_refs(cls: type[M]) -> None:
        cls.update_forward_refs()

    def iter_fields(obj: type[M]) -> Iterator[tuple[str, ModelField]]:  # type: ignore
        yield from obj.__fields__.items()  # type: ignore

    def model_config(**kwargs: Any) -> dict | type:
        return type("Config", (), kwargs)

    def _get_metadata(pydantic_field) -> dict:  # type: ignore
        extra = pydantic_field.field_info.extra
        if "json_schema_extra" in extra:
            return extra["json_schema_extra"]
        return extra.get("metadata", {})

    def fields_set(obj: BaseModel) -> set[str]:
        return obj.__fields_set__


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
    for name, f in iter_fields(obj):
        yield _pydantic_field_to_dataclass_field(name, f)
