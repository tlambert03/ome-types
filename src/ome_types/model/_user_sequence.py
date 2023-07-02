from typing import Iterable, List, MutableSequence, TypeVar, Union, overload

T = TypeVar("T")


class UserSequence(MutableSequence[T]):
    """Generric Mutable sequence, that expects the real list at __root__."""

    __root__: List[object]

    def __repr__(self) -> str:
        return repr(self.__root__)

    def __delitem__(self, _idx: Union[int, slice]) -> None:
        del self.__root__[_idx]

    @overload
    def __getitem__(self, _idx: int) -> T:
        ...

    @overload
    def __getitem__(self, _idx: slice) -> List[T]:
        ...

    def __getitem__(self, _idx: Union[int, slice]) -> Union[T, List[T]]:
        return self.__root__[_idx]  # type: ignore[return-value]

    def __len__(self) -> int:
        return super().__len__()

    @overload
    def __setitem__(self, _idx: int, _val: T) -> None:
        ...

    @overload
    def __setitem__(self, _idx: slice, _val: Iterable[T]) -> None:
        ...

    def __setitem__(self, _idx: Union[int, slice], _val: Union[T, Iterable[T]]) -> None:
        self.__root__[_idx] = _val  # type: ignore[index]

    def insert(self, index: int, value: T) -> None:
        self.__root__.insert(index, value)

    # for some reason, without overloading this... append() adds things to the
    # beginning of the list instead of the end
    def append(self, value: T) -> None:
        self.__root__.append(value)
