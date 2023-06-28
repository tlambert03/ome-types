import contextlib
from datetime import datetime
from enum import Enum
from textwrap import indent
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Sequence, Set, Type, cast

import pydantic
from pydantic import BaseModel, ValidationError, validator

from ome_types.units import ureg

if TYPE_CHECKING:
    import pint


class Sentinel:
    """Create singleton sentinel objects with a readable repr."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"{__name__}.{self.name}.{id(self):x}"


# Default value to support automatic numbering for id field values.
_AUTO_SEQUENCE = Sentinel("AUTO_SEQUENCE")
_COUNTERS: dict[Type["OMEType"], int] = {}
_UNIT_FIELD = "{}_unit"
_QUANTITY_FIELD = "{}_quantity"


class OMEType(BaseModel):
    """The base class that all OME Types inherit from.

    This provides some global conveniences around auto-setting ids. (i.e., making them
    optional in the class constructor, but never ``None`` after initialization.).
    It provides a nice __repr__ that hides things that haven't been changed from
    defaults.  It adds ``*_quantity`` property for fields that have both a value and a
    unit, where ``*_quantity`` is a pint ``Quantity``.  It also provides pickling
    support.
    """

    # pydantic BaseModel configuration.
    # see: https://pydantic-docs.helpmanual.io/usage/model_config/
    class Config:
        arbitrary_types_allowed = False
        validate_assignment = True
        underscore_attrs_are_private = True
        use_enum_values = False
        validate_all = True

    # allow use with weakref
    __slots__: ClassVar[Set[str]] = {"__weakref__"}  # type: ignore

    def __init__(__pydantic_self__, **data: Any) -> None:
        if "id" in __pydantic_self__.__fields__:
            data.setdefault("id", _AUTO_SEQUENCE)
        try:
            super().__init__(**data)
        except ValidationError as e:
            for err in e.raw_errors:
                if isinstance(err, pydantic.error_wrappers.ErrorWrapper):
                    loc = err.loc_tuple()
                    if loc:
                        key = loc[0]
                        if key == "id":
                            data[key] = _AUTO_SEQUENCE
                        else:
                            data.pop(key, None)
            print(data)
            super().__init__(**data)

    def __init_subclass__(cls) -> None:
        """Add `*_quantity` property for fields that have both a value and a unit.

        where `*_quantity` is a pint `Quantity`.
        """
        for field in cls.__fields__:
            if _UNIT_FIELD.format(field) in cls.__fields__:
                setattr(cls, _QUANTITY_FIELD.format(field), _quantity_property(field))

    def __repr__(self) -> str:
        name = self.__class__.__qualname__
        lines = []
        for f in sorted(
            self.__fields__.values(), key=lambda f: f.name not in ("name", "id")
        ):
            if f.name.endswith("_"):
                continue
            # https://github.com/python/mypy/issues/6910
            default = f.default_factory() if f.default_factory else f.default
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
        return f"{name}({body})"

    @validator("id", pre=True, always=True, check_fields=False)
    @classmethod
    def validate_id(cls, value: Any) -> Any:
        """Pydantic validator for ID fields in OME models.

        If no value is provided, this validator provides and integer ID, and stores the
        maximum previously-seen value on the class.
        """
        # get the required LSID field from the annotation
        current_count = _COUNTERS.setdefault(cls, 0)
        if isinstance(value, str):
            # parse the id and update the counter
            v_id = value.rsplit(":", 1)[-1]
            with contextlib.suppress(ValueError):
                _COUNTERS[cls] = max(current_count, int(v_id))
            return value
        if isinstance(value, int):
            _COUNTERS[cls] = max(current_count, value)
            return f"{cls.__name__}:{value}"

        if value is _AUTO_SEQUENCE:
            # just increment the counter
            _COUNTERS[cls] += 1
            return f"{cls.__name__}:{_COUNTERS[cls]}"

        raise ValueError(f"Invalid ID value: {value!r}")

    # @classmethod
    # def snake_name(cls) -> str:
    #     from .model import _camel_to_snake

    #     return _camel_to_snake[cls.__name__]


def _quantity_property(field_name: str) -> property:
    """Create property that returns a ``pint.Quantity`` combining value and unit."""

    def quantity(self: Any) -> Optional["pint.Quantity"]:
        value = getattr(self, field_name)
        if value is None:
            return None

        unit = cast("Enum", getattr(self, _UNIT_FIELD.format(field_name)))
        return ureg.Quantity(value, unit.value.replace(" ", "_"))

    return property(quantity)
