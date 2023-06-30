from typing import TYPE_CHECKING, Any, Dict, Optional

from ._base_type import OMEType

if TYPE_CHECKING:
    import weakref


class ReferenceMixin(OMEType):
    _ref: Optional["weakref.ReferenceType[OMEType]"] = None

    @property
    def ref(self) -> "OMEType | None":
        if self._ref is None:
            raise ValueError("references not yet resolved on root OME object")
        return self._ref()

    def __getstate__(self: Any) -> Dict[str, Any]:
        """Support pickle of our weakref references."""
        state = super().__getstate__()
        state["__private_attribute_values__"].pop("_ref", None)
        return state
