from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import ExperimenterGroupID


class ExperimenterGroupRef(Reference, OMEType):
    """This empty element has a reference (the ExperimenterGroup ID attribute) to a
    ExperimenterGroup defined within OME.

    Parameters
    ----------
    id : ExperimenterGroupID
    """

    id: ExperimenterGroupID
