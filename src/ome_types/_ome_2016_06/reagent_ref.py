from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import ReagentID


class ReagentRef(Reference, OMEType):
    """ReagentRef.

    Parameters
    ----------
    id : ReagentID
    """

    id: ReagentID
