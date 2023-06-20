from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import FilterID


class FilterRef(Reference, OMEType):
    """FilterRef.

    Parameters
    ----------
    id : FilterID
    """

    id: FilterID
