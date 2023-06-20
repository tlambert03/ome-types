from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import ExperimentID


class ExperimentRef(Reference, OMEType):
    """ExperimentRef.

    Parameters
    ----------
    id : ExperimentID
    """

    id: ExperimentID
