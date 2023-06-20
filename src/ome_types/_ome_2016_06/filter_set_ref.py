from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import FilterSetID


class FilterSetRef(Reference, OMEType):
    """FilterSetRef.

    Parameters
    ----------
    id : FilterSetID
    """

    id: FilterSetID
