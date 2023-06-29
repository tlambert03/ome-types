from typing import TYPE_CHECKING, Iterable, Sequence

from ome_types.model.ome_2016_06 import Annotation

from ._base_type import OMEType

if TYPE_CHECKING:
    from ome_types.model.ome_2016_06 import StructuredAnnotations


class StructuredAnnotationsMixin(OMEType, Sequence):
    def _iter_annotations(self: "StructuredAnnotations") -> Iterable[Annotation]:
        for x in self.__fields__.values():
            if issubclass(x.type_, Annotation):
                yield from getattr(self, x.name)
            else:
                breakpoint()

    def __getitem__(self: "StructuredAnnotations", key) -> Annotation:
        return list(self._iter_annotations())[key]

    def __len__(self) -> int:
        return len(list(self._iter_annotations()))

    def append(self: "StructuredAnnotations", value: Annotation) -> None:
        raise NotImplementedError
