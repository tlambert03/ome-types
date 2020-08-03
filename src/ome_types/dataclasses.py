from __future__ import annotations
from pydantic.dataclasses import _process_class
from pydantic import validator

from typing import TYPE_CHECKING, Any, Callable, Optional, Type, Union


if TYPE_CHECKING:
    from pydantic.dataclasses import DataclassType


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
    if "id" in getattr(_cls, "__annotations__", {}):
        setattr(_cls, "validate_id", validate_id)
        if not hasattr(_cls, "id"):
            setattr(_cls, "id", None)

    def wrap(cls: Type[Any]) -> DataclassType:
        return _process_class(cls, init, repr, eq, order, unsafe_hash, frozen, config)

    return wrap if _cls is None else wrap(_cls)
