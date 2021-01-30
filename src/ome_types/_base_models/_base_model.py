from datetime import datetime
from enum import Enum
from textwrap import indent
from typing import Any, Sequence

from pydantic import BaseModel, validator


class Sentinel:
    """Create singleton sentinel objects with a readable repr."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"{__name__}.{self.name}"


# Default value to support optional fields in dataclass subclasses.
EMPTY = Sentinel("EMPTY")
# Default value to support automatic numbering for id field values.
AUTO_SEQUENCE = Sentinel("AUTO_SEQUENCE")


class BaseOMEModel(BaseModel):

    # __slots__: ClassVar[Set[str]] = {"__weakref__"}  # type: ignore

    # pydantic BaseModel configuration.  see:
    # https://pydantic-docs.helpmanual.io/usage/model_config/
    class Config:
        # whether to allow arbitrary user types for fields (they are validated
        # simply by checking if the value is an instance of the type). If
        # False, RuntimeError will be raised on model declaration
        arbitrary_types_allowed = True
        # whether to perform validation on assignment to attributes
        validate_assignment = True
        # whether to treat any underscore non-class var attrs as private
        # https://pydantic-docs.helpmanual.io/usage/models/#private-model-attributes
        underscore_attrs_are_private = True
        # whether to populate models with the value property of enums, rather
        # than the raw enum. This may be useful if you want to serialise
        # model.dict() later
        use_enum_values = True
        # whether to validate field defaults (default: False)
        validate_all = True
        # a dict used to customise the way types are encoded to JSON
        # https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeljson

    def __repr__(self: Any) -> str:
        name = self.__class__.__qualname__
        lines = []
        for f in sorted(
            self.__fields__.values(), key=lambda f: f.name not in ("name", "id")
        ):
            if f.name.endswith("_"):
                continue
            # https://github.com/python/mypy/issues/6910
            if f.default_factory:
                default = f.default_factory()
            else:
                default = f.default

            current = getattr(self, f.name)
            if current != default:
                if isinstance(current, Sequence) and not isinstance(current, str):
                    rep = f"[<{len(current)} {f.name.title()}>]"
                elif isinstance(current, Enum):
                    rep = repr(current.value)
                elif isinstance(current, datetime):
                    rep = f"datetime.fromisoformat({current.isoformat()!r})"
                else:
                    rep = repr(current)
                lines.append(f"{f.name}={rep},")
        if len(lines) == 1:
            body = lines[-1].rstrip(",")
        elif lines:
            body = "\n" + indent("\n".join(lines), "   ") + "\n"
        else:
            body = ""
        out = f"{name}({body})"
        return out

    @validator("id", pre=True, always=True, check_fields=False)
    def validate_id(cls, value: Any) -> str:
        """Pydantic validator for ID fields in OME dataclasses.

        If no value is provided, this validator provides and integer ID, and stores the
        maximum previously-seen value on the class.
        """
        from typing import ClassVar

        # get the required LSID type from the annotation
        id_type = cls.__annotations__.get("id")
        if not id_type:
            return value

        # Store the highest seen value on the class._max_id attribute.
        if not hasattr(cls, "_max_id"):
            cls._max_id = 0
            cls.__annotations__["_max_id"] = ClassVar[int]

        if value is AUTO_SEQUENCE:
            value = cls._max_id + 1
        if isinstance(value, int):
            v_id = value
            id_string = id_type.__name__[:-2]
            value = f"{id_string}:{value}"
        else:
            value = str(value)
            v_id = value.rsplit(":", 1)[-1]
        try:
            v_id = int(v_id)
            cls._max_id = max(cls._max_id, v_id)
        except ValueError:
            pass

        return id_type(value)
