from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import ExperimenterID


class ExperimenterRef(Reference, OMEType):
    """This empty element has a required Experimenter ID and an optional DocumentID
    attribute which refers to one of the Experimenters defined within OME.

    Parameters
    ----------
    id : ExperimenterID
    """

    id: ExperimenterID
