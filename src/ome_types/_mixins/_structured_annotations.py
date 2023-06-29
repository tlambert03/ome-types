from typing import Iterable, Sequence, TypeVar, overload

from ome_types.model.ome_2016_06 import Annotation

from ._base_type import OMEType

_T_co = TypeVar("_T_co", covariant=True)  # Any type covariant containers.


class StructuredAnnotationsMixin(OMEType, Sequence[Annotation]):  # type: ignore
    def _iter_annotations(self) -> Iterable[Annotation]:
        for x in self.__fields__.values():
            if issubclass(x.type_, Annotation):
                yield from getattr(self, x.name)

    @overload
    def __getitem__(self, index: int) -> Annotation:
        ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Annotation]:
        ...

    def __getitem__(self, key: int | slice) -> Annotation | Sequence[Annotation]:
        return list(self._iter_annotations())[key]

    def __len__(self) -> int:
        return len(list(self._iter_annotations()))
