from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Optional, Type, Union

from pydantic import validator
from pydantic.dataclasses import _process_class

if TYPE_CHECKING:
    from pydantic.dataclasses import DataclassType

EMPTY = object()


@validator("id", pre=True, always=True)
def validate_id(cls: Type[Any], value: Any) -> str:
    from typing import ClassVar, Union

    # get the required LSID type from the annotation
    id_type = cls.__annotations__.get("id")
    # (it will likely be an Optional[LSID])
    if getattr(id_type, "__origin__", None) is Union:
        id_type = getattr(id_type, "__args__")[0]
    if not id_type:
        return value

    if not hasattr(cls, "_max_id"):
        cls._max_id = 0
        cls.__annotations__["_max_id"] = ClassVar[int]

    if not value:
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


def ome_dataclass(
    _cls: Optional[Type[Any]] = None,
    *,
    init: bool = True,
    repr: bool = True,
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
        if "id" in getattr(cls, "__annotations__", {}):
            setattr(cls, "validate_id", validate_id)
            if not hasattr(cls, "id"):
                setattr(cls, "id", None)

        modify_post_init(cls)

        return _process_class(cls, init, repr, eq, order, unsafe_hash, frozen, config)

    return wrap if _cls is None else wrap(_cls)


__all__ = ["EMPTY", "ome_dataclass"]
