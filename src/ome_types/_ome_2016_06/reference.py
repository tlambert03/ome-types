from typing import TYPE_CHECKING, Any, Optional
from weakref import ReferenceType

from ome_types._base_type import OMEType

from .simple_types import LSID


class Reference(OMEType):
    """Reference is an empty complex type that is contained and extended by all the
    `*Ref` elements and also the Settings Complex Type Each `*Ref` element defines
    an attribute named ID of simple type `*ID` and no other information Each
    simple type `*ID` is restricted to the base type LSID with an appropriate
    pattern
    """

    if TYPE_CHECKING:
        _ref: Optional["ReferenceType[OMEType]"]

    id: LSID
    _ref = None

    @property
    def ref(self) -> Any:
        if self._ref is None:
            raise ValueError("references not yet resolved on root OME object")
        return self._ref()
