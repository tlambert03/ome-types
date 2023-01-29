from typing import TYPE_CHECKING, Any, ClassVar, Dict, Optional, Sequence, Set

from pydantic import BaseModel, validator

if TYPE_CHECKING:
    import pint


class Sentinel:
    """Create singleton sentinel objects with a readable repr."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"{__name__}.{self.name}.{id(self)}"


def quantity_property(field: str) -> property:
    """Create property that returns a ``pint.Quantity`` combining value and unit."""

    def quantity(self: Any) -> Optional["pint.Quantity"]:
        from ome_types._units import ureg

        value = getattr(self, field)
        if value is None:
            return None
        unit = getattr(self, f"{field}_unit").value.replace(" ", "_")
        return ureg.Quantity(value, unit)

    return property(quantity)


class OMEType(BaseModel):
    """The base class that all OME Types inherit from.

    This provides some global conveniences around auto-setting ids. (i.e., making them
    optional in the class constructor, but never ``None`` after initialization.).
    It provides a nice __repr__ that hides things that haven't been changed from
    defaults.  It adds ``*_quantity`` property for fields that have both a value and a
    unit, where ``*_quantity`` is a pint ``Quantity``.  It also provides pickling
    support.
    """

    # Default value to support automatic numbering for id field values.
    _AUTO_SEQUENCE = Sentinel("AUTO_SEQUENCE")
    # allow use with weakref
    __slots__: ClassVar[Set[str]] = {"__weakref__"}  # type: ignore

    def __init__(__pydantic_self__, **data: Any) -> None:
        if "id" in __pydantic_self__.__fields__:
            data.setdefault("id", OMEType._AUTO_SEQUENCE)
        super().__init__(**data)

    def __init_subclass__(cls) -> None:
        """Add some properties to subclasses with units.

        It adds ``*_quantity`` property for fields that have both a value and a
        unit, where ``*_quantity`` is a pint ``Quantity``
        """
        _clsdir = set(cls.__fields__)
        for field in _clsdir:
            if f"{field}_unit" in _clsdir:
                setattr(cls, f"{field}_quantity", quantity_property(field))

    # pydantic BaseModel configuration.
    # see: https://pydantic-docs.helpmanual.io/usage/model_config/
    class Config:
        # whether to allow arbitrary user types for fields (they are validated
        # simply by checking if the value is an instance of the type). If
        # False, RuntimeError will be raised on model declaration
        arbitrary_types_allowed = False
        # whether to perform validation on assignment to attributes
        validate_assignment = True
        # whether to treat any underscore non-class var attrs as private
        # https://pydantic-docs.helpmanual.io/usage/models/#private-model-attributes
        underscore_attrs_are_private = True
        # whether to populate models with the value property of enums, rather
        # than the raw enum. This may be useful if you want to serialise
        # model.dict() later.  False by default
        # see conversation in https://github.com/tlambert03/ome-types/pull/74
        use_enum_values = False
        # whether to validate field defaults (default: False)
        validate_all = True

    def __repr__(self: Any) -> str:
        from datetime import datetime
        from enum import Enum
        from textwrap import indent

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
        """Pydantic validator for ID fields in OME models.

        If no value is provided, this validator provides and integer ID, and stores the
        maximum previously-seen value on the class.
        """
        from typing import ClassVar

        # get the required LSID field from the annotation
        id_field = cls.__fields__.get("id")
        if not id_field:
            return value

        # Store the highest seen value on the class._max_id attribute.
        if not hasattr(cls, "_max_id"):
            cls._max_id = 0  # type: ignore [misc]
            cls.__annotations__["_max_id"] = ClassVar[int]
        if value is OMEType._AUTO_SEQUENCE:
            value = cls._max_id + 1
        if isinstance(value, int):
            v_id = value
            id_string = id_field.type_.__name__[:-2]
            value = f"{id_string}:{value}"
        else:
            value = str(value)
            v_id = value.rsplit(":", 1)[-1]
        try:
            v_id = int(v_id)
            cls._max_id = max(cls._max_id, v_id)  # type: ignore [misc]
        except ValueError:
            pass

        return id_field.type_(value)

    def __getstate__(self: Any) -> Dict[str, Any]:
        """Support pickle of our weakref references."""
        state = super().__getstate__()
        state["__private_attribute_values__"].pop("_ref", None)
        return state

    @classmethod
    def snake_name(cls) -> str:
        from .model import _camel_to_snake

        return _camel_to_snake[cls.__name__]
