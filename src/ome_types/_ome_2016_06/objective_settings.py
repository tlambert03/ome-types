from enum import Enum
from typing import Optional

from ome_types._base_type import OMEType

from .settings import Settings
from .simple_types import ObjectiveID


class Medium(Enum):
    AIR = "Air"
    GLYCEROL = "Glycerol"
    OIL = "Oil"
    OTHER = "Other"
    WATER = "Water"


class ObjectiveSettings(Settings, OMEType):
    """This holds the setting applied to an objective as well as a reference to the
    objective.

    The ID is the objective used in this case.

    Parameters
    ----------
    id : ObjectiveID
    correction_collar : float, optional
        The CorrectionCollar is normally an adjustable ring on the objective.
        Each has an arbitrary scale on it so the values is unit-less.
    medium : Medium, optional
    refractive_index : float, optional
        The RefractiveIndex is that of the immersion medium. This is a ratio
        so it also unit-less.
    """

    id: ObjectiveID
    correction_collar: Optional[float] = None
    medium: Optional[Medium] = None
    refractive_index: Optional[float] = None
