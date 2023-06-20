from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import ExperimenterID


class Leader(Reference, OMEType):
    """Contact information for a ExperimenterGroup leader specified using a reference
    to an Experimenter element defined elsewhere in the document.

    Parameters
    ----------
    id : ExperimenterID
    """

    id: ExperimenterID
