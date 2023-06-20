from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import LightSourceID


class Pump(Reference, OMEType):
    """The Pump element is a reference to a LightSource.

    It is used within the Laser element to specify the light source for the
    laser's pump (if any).

    Parameters
    ----------
    id : LightSourceID
    """

    id: LightSourceID
