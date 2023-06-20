from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import MicrobeamManipulationID


class MicrobeamManipulationRef(Reference, OMEType):
    """MicrobeamManipulationRef.

    Parameters
    ----------
    id : MicrobeamManipulationID
    """

    id: MicrobeamManipulationID
