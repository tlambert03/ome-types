from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import ROIID


class ROIRef(Reference, OMEType):
    """ROIRef.

    Parameters
    ----------
    id : ROIID
    """

    id: ROIID
