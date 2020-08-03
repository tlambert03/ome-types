from __future__ import annotations
from pydantic.dataclasses import _process_class
from pydantic import validator

from typing import TYPE_CHECKING, Any, Callable, Optional, Type, Union


if TYPE_CHECKING:
    from pydantic.dataclasses import DataclassType


@validator("id", pre=True, always=True)
def validate_id(cls: Type[Any], value: Any) -> str:
    from typing import ClassVar, Set, Union

    # get the required LSID type from the annotation
    id_type = cls.__annotations__.get("id")
    # (it will likely be an Optional[LSID])
    if getattr(id_type, "__origin__", None) is Union:
        id_type = getattr(id_type, "__args__")[0]
    if not id_type:
        return value

    if not hasattr(cls, "_global_ids"):
        cls._global_ids = set()
        cls.__annotations__["_global_ids"] = ClassVar[Set[str]]

    id_string = id_type.__name__[:-2]
    if not value:
        suffixes = [i.split(":")[-1] for i in cls._global_ids]
        max_id = max({int(s) for s in suffixes if s.isdigit()} or {0})
        new_id = f"{id_string}:{max_id + 1}"
    else:
        new_id = f"{id_string}:{value}" if isinstance(value, int) else str(value)

    cls._global_ids.add(new_id)
    return id_type(new_id)


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
