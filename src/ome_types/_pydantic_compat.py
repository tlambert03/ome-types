from __future__ import annotations

from typing import TYPE_CHECKING, Any, MutableSequence, cast

import pydantic.version
from pydantic import BaseModel

if TYPE_CHECKING:
    from pydantic.fields import FieldInfo

pydantic_version: tuple[int, ...] = tuple(
    int(x) for x in pydantic.version.VERSION.split(".")[:2]
)


if pydantic_version >= (2,):
    try:
        from pydantic_extra_types.color import Color as Color
    except ImportError:
        from pydantic.color import Color as Color

    def field_type(field: FieldInfo) -> Any:
        return field.annotation

    def field_regex(obj: type[BaseModel], field_name: str) -> str | None:
        # typing is incorrect at the moment, but may indicate breakage in pydantic 3
        field_info = obj.model_fields[field_name]  # type: ignore [index]
        meta = field_info.json_schema_extra or {}
        # if a "metadata" key exists... use it.
        # After pydantic-compat 0.2, this is where it will be.
        if "metadata" in meta:  # type: ignore
            meta = meta["metadata"]  # type: ignore
        if meta:
            return meta.get("pattern")  # type: ignore
        return None

    kw: dict = {"validated_data": {}} if pydantic_version >= (2, 10) else {}

    def get_default(f: FieldInfo) -> Any:
        return f.get_default(call_default_factory=True, **kw)
else:
    from pydantic.color import Color as Color  # type: ignore [no-redef]

    def field_type(field: Any) -> Any:  # type: ignore
        return field.type_

    def field_regex(obj: type[BaseModel], field_name: str) -> str | None:
        field = obj.__fields__[field_name]  # type: ignore
        return cast(str, field.field_info.regex)

    def get_default(f: Any) -> Any:  # type: ignore
        return f.get_default()


def update_set_fields(self: BaseModel) -> None:
    """Update set fields with populated mutable sequences.

    Because pydantic isn't aware of mutations to sequences, it can't tell when
    a field has been "set" by mutating a sequence.  This method updates the
    self.__fields_set__ attribute to reflect that.  We assume that if an attribute
    is not None, and is not equal to the default value, then it has been set.
    """
    for field_name, field in self.model_fields.items():
        current = getattr(self, field_name)
        if not current:
            continue
        if current != get_default(field):
            self.model_fields_set.add(field_name)
        if isinstance(current, BaseModel):
            update_set_fields(current)
        if isinstance(current, MutableSequence):
            for item in current:
                if isinstance(item, BaseModel):
                    update_set_fields(item)
