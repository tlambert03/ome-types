from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import ChannelID


class ChannelRef(Reference, OMEType):
    """ChannelRef.

    Parameters
    ----------
    id : ChannelID
    """

    id: ChannelID
