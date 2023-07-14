from typing import Iterable, List, MutableSequence, TypeVar, Union, overload

import pydantic.version

T = TypeVar("T")

if pydantic.version.VERSION.startswith("2"):
    ROOT_NAME = "root"
else:
    ROOT_NAME = "__root__"


class UserSequence(MutableSequence[T]):
    """Generric Mutable sequence, that expects the real list at __root__."""

    if pydantic.version.VERSION.startswith("2"):
        root: List[object]
    else:
        __root__: List[object]

    def __repr__(self) -> str:
        return repr(getattr(self, ROOT_NAME))

    def __delitem__(self, _idx: Union[int, slice]) -> None:
        del getattr(self, ROOT_NAME)[_idx]

    @overload
    def __getitem__(self, _idx: int) -> T:
        ...

    @overload
    def __getitem__(self, _idx: slice) -> List[T]:
        ...

    def __getitem__(self, _idx: Union[int, slice]) -> Union[T, List[T]]:
        return getattr(self, ROOT_NAME)[_idx]  # type: ignore[return-value]

    def __len__(self) -> int:
        return len(getattr(self, ROOT_NAME))

    @overload
    def __setitem__(self, _idx: int, _val: T) -> None:
        ...

    @overload
    def __setitem__(self, _idx: slice, _val: Iterable[T]) -> None:
        ...

    def __setitem__(self, _idx: Union[int, slice], _val: Union[T, Iterable[T]]) -> None:
        getattr(self, ROOT_NAME)[_idx] = _val  # type: ignore[index]

    def insert(self, index: int, value: T) -> None:
        getattr(self, ROOT_NAME).insert(index, value)

    # for some reason, without overloading this... append() adds things to the
    # beginning of the list instead of the end
    def append(self, value: T) -> None:
        getattr(self, ROOT_NAME).append(value)
