from __future__ import annotations

from typing import Any, Callable, MutableSequence, cast

import pydantic.version
from pydantic import BaseModel

PYDANTIC2 = pydantic.version.VERSION.startswith("2")

if PYDANTIC2:
    from pydantic import functional_validators, model_validator
    from pydantic.fields import FieldInfo

    def model_fields(obj: BaseModel | type[BaseModel]) -> dict[str, FieldInfo]:
        return obj.model_fields

    def field_regex(obj: type[BaseModel], field_name: str) -> str | None:
        field_info = obj.model_fields[field_name]
        if field_info.json_schema_extra:
            return field_info.json_schema_extra.get("pattern")
        return None

    def fields_set(obj: BaseModel) -> set[str]:
        return obj.model_fields_set

    def field_validator(*args: Any, **kwargs: Any) -> Callable[[Callable], Callable]:
        return functional_validators.field_validator(*args, **kwargs)

    def field_type(field: FieldInfo):
        return field.annotation

    def get_default(f: FieldInfo) -> Any:
        return f.get_default(call_default_factory=True)

    def model_dump(obj: BaseModel, **kwargs: Any) -> dict[str, Any]:
        return obj.model_dump(**kwargs)

else:
    from pydantic.fields import ModelField, root_validator, validator

    def model_fields(obj: BaseModel | type[BaseModel]) -> dict[str, ModelField]:
        return obj.__fields__

    def field_type(field: ModelField):
        return field.type_

    def field_regex(obj: type[BaseModel], field_name: str) -> str | None:
        field = obj.__fields__[field_name]
        return cast(str, field.field_info.regex)

    def fields_set(obj: BaseModel) -> set[str]:
        return obj.__fields_set__

    def model_validator(**kwargs):
        if kwargs.get("mode") == "before":
            return root_validator(pre=True)
        return root_validator(pre=False)

    def field_validator(**kwargs: Any) -> Callable[[Callable], Callable]:
        if kwargs.get("mode") == "before":
            return validator(pre=True)
        return validator()

    def get_default(f: ModelField) -> Any:
        return f.get_default()

    def model_dump(obj: BaseModel, **kwargs: Any) -> dict[str, Any]:
        return obj.dict(**kwargs)


def update_set_fields(self: BaseModel) -> None:
    """Update set fields with populated mutable sequences.

    Because pydantic isn't aware of mutations to sequences, it can't tell when
    a field has been "set" by mutating a sequence.  This method updates the
    self.__fields_set__ attribute to reflect that.  We assume that if an attribute
    is not None, and is not equal to the default value, then it has been set.
    """
    for field_name, field in model_fields(self).items():
        current = getattr(self, field_name)
        if not current:
            continue
        if current != get_default(field):
            fields_set(self).add(field_name)
        if isinstance(current, BaseModel):
            update_set_fields(current)
        if isinstance(current, MutableSequence):
            for item in current:
                if isinstance(item, BaseModel):
                    update_set_fields(item)
