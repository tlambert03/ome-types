from typing import Iterator, Sequence, overload

from ome_types.model.ome_2016_06 import Annotation

from ._base_type import OMEType


class StructuredAnnotationsMixin(OMEType, Sequence[Annotation]):
    def _iter_annotations(self) -> Iterator[Annotation]:
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

    def __iter__(self) -> Iterator[Annotation]:  # type: ignore[override]
        return self._iter_annotations()
