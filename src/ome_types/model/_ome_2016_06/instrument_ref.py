from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import InstrumentID


class InstrumentRef(Reference, OMEType):
    """This empty element can be used (via the required Instrument ID attribute) to
    refer to an Instrument defined within OME.

    Parameters
    ----------
    id : InstrumentID
    """

    id: InstrumentID
