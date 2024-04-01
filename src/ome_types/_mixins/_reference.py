import weakref
from typing import Any, Dict, Optional, Union

from pydantic import PrivateAttr
from some_types._mixins._base_type import SOMEType


class ReferenceMixin(SOMEType):
    _ref: Optional[weakref.ReferenceType] = PrivateAttr(None)

    @property
    def ref(self) -> Union[SOMEType, None]:
        if self._ref is None:
            raise ValueError("references not yet resolved on root SOME object")
        return self._ref()

    def __getstate__(self: Any) -> Dict[str, Any]:
        """Support pickle of our weakref references."""
        state = super().__getstate__()
        if "__private_attribute_values__" in state:
            state["__private_attribute_values__"].pop("_ref", None)
        elif "__pydantic_private__" in state:
            state["__pydantic_private__"].pop("_ref", None)
        return state
