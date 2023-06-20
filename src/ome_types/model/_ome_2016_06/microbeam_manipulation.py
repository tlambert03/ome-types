from enum import Enum
from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .experimenter_ref import ExperimenterRef
from .light_source_settings import LightSourceSettings
from .roi_ref import ROIRef
from .simple_types import MicrobeamManipulationID


class Type(Enum):
    """The type of manipulation performed."""

    FLIP = "FLIP"
    FRAP = "FRAP"
    INVERSE_FRAP = "InverseFRAP"
    OPTICAL_TRAPPING = "OpticalTrapping"
    OTHER = "Other"
    PHOTOABLATION = "Photoablation"
    PHOTOACTIVATION = "Photoactivation"
    UNCAGING = "Uncaging"


class MicrobeamManipulation(OMEType):
    """Defines a microbeam operation type and the region of the image it was applied
    to.

    The LightSourceRef element is a reference to a LightSource specified in the
    Instrument element which was used for a technique other than illumination for
    the purpose of imaging. For example, a laser used for photobleaching.

    Parameters
    ----------
    experimenter_ref : ExperimenterRef
    id : MicrobeamManipulationID
    roi_ref : ROIRef
    description : str, optional
        A description for the Microbeam Manipulation.
    light_source_settings : LightSourceSettings, optional
    type : Type, optional
        The type of manipulation performed.
    """

    experimenter_ref: ExperimenterRef
    id: MicrobeamManipulationID
    roi_ref: List[ROIRef]
    description: Optional[str] = None
    light_source_settings: List[LightSourceSettings] = Field(default_factory=list)
    type: List[Type] = Field(default_factory=list)
