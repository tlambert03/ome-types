from __future__ import annotations

from dataclasses import MISSING, fields
from datetime import datetime
from enum import Enum
from textwrap import indent
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Sequence, Type, Union

import pint
from pydantic import validator
from pydantic.dataclasses import _process_class

if TYPE_CHECKING:
    from pydantic.dataclasses import DataclassType


ureg = pint.UnitRegistry(auto_reduce_dimensions=True)
ureg.define("reference_frame = [_reference_frame]")
ureg.define("@alias grade = gradian")
ureg.define("@alias astronomical_unit = ua")
ureg.define("line = inch / 12 = li")


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


@validator("id", pre=True, always=True)
def validate_id(cls: Type[Any], value: Any) -> str:
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


def modify_post_init(_cls: Type[Any]) -> None:
    """Modify __post_init__.

    Provides support for non-default arguments in dataclass subclasses (where the super
    class has default args) by providing the default value "EMPTY" from this module.
    """
    origin_post_init = getattr(_cls, "__post_init__", None)
    required_fields = {k for k, v in _cls.__dict__.items() if v is EMPTY}

    def new_post_init(self: Any, *args: Any) -> None:
        missed = {f for f in required_fields if getattr(self, f, None) is EMPTY}
        if missed:
            nmissed = len(missed)
            s = "s" if nmissed > 1 else ""
            raise TypeError(
                f"__init__ missing {nmissed} required argument{s}: {sorted(missed)!r}"
            )
        if origin_post_init is not None:
            origin_post_init(self, *args)

    setattr(_cls, "__post_init__", new_post_init)


def add_quantities(_cls: Type[Any]) -> None:
    value_fields = [f for f in dir(_cls) if f + "_unit" in dir(_cls)]
    for field in value_fields:
        setattr(_cls, field + "_quantity", quantity_property(field))


def quantity_property(field: str) -> property:
    def quantity(self: Any) -> Optional[pint.Quantity]:
        value = getattr(self, field)
        if value is None:
            return None
        unit = getattr(self, field + "_unit").value.replace(" ", "_")
        return ureg.Quantity(value, unit)

    return property(quantity)


def modify_repr(_cls: Type[Any]) -> None:
    """Improved dataclass repr function.

    Only show non-default non-internal values, and summarize containers.
    """
    # let classes still create their own
    if _cls.__repr__ is not object.__repr__:
        return

    def new_repr(self: Any) -> str:
        name = self.__class__.__qualname__
        lines = []
        for f in sorted(fields(self), key=lambda f: f.name not in ("name", "id")):
            if f.name.endswith("_"):
                continue
            # https://github.com/python/mypy/issues/6910
            if f.default_factory is not MISSING:  # type: ignore
                default = f.default_factory()  # type: ignore
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

    setattr(_cls, "__repr__", new_repr)


def __getstate__(self: Any) -> Dict[str, Any]:
    """Support pickle of our weakref references."""
    # don't do copy unless necessary
    if "ref_" in self.__dict__:
        d = self.__dict__.copy()
        del d["ref_"]  # remove weakref
        return d
    return self.__dict__


def ome_dataclass(
    _cls: Optional[Type[Any]] = None,
    *,
    init: bool = True,
    repr: bool = False,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
    config: Type[Any] = None,
) -> Union[Callable[[Type[Any]], DataclassType], DataclassType]:
    """Wrapper on the pydantic dataclass decorator.

    Provides OME-specific methods and validators.
    """

    def wrap(cls: Type[Any]) -> DataclassType:
        if getattr(cls, "id", None) is AUTO_SEQUENCE:
            setattr(cls, "validate_id", validate_id)
        modify_post_init(cls)
        if not hasattr(cls, "__getstate__"):
            cls.__getstate__ = __getstate__
        add_quantities(cls)
        if not repr:
            modify_repr(cls)
        return _process_class(cls, init, repr, eq, order, unsafe_hash, frozen, config)

    return wrap if _cls is None else wrap(_cls)


__all__ = ["EMPTY", "ome_dataclass"]
