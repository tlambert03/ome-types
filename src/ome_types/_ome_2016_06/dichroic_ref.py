from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import DichroicID


class DichroicRef(Reference, OMEType):
    """DichroicRef.

    Parameters
    ----------
    id : DichroicID
    """

    id: DichroicID
