import weakref
from typing import Any, Dict, Optional, Union

from ome_types._mixins._base_type import OMEType


class ReferenceMixin(OMEType):
    _ref: Optional[weakref.ReferenceType] = None

    @property
    def ref(self) -> Union[OMEType, None]:
        if self._ref is None:
            raise ValueError("references not yet resolved on root OME object")
        return self._ref()

    def __getstate__(self: Any) -> Dict[str, Any]:
        """Support pickle of our weakref references."""
        state = super().__getstate__()
        state["__private_attribute_values__"].pop("_ref", None)
        return state
