import weakref
from typing import Optional

from ._base_type import OMEType


class ReferenceMixin(OMEType):
    _ref: Optional[weakref.ReferenceType["OMEType"]] = None

    @property
    def ref(self) -> "OMEType | None":
        if self._ref is None:
            raise ValueError("references not yet resolved on root OME object")
        return self._ref()
