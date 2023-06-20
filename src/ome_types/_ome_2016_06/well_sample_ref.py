from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import WellSampleID


class WellSampleRef(Reference, OMEType):
    """The WellSampleRef element is a reference to a WellSample element.

    Parameters
    ----------
    id : WellSampleID
    """

    id: WellSampleID
