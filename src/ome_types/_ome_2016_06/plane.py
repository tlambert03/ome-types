from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .simple_types import Hex40, NonNegativeInt, UnitsLength, UnitsTime


class Plane(OMEType):
    """The Plane object holds microscope stage and image timing data for a given
    channel/z-section/timepoint.

    Parameters
    ----------
    the_c : NonNegativeInt
        The channel this plane is for. This is numbered from 0.
    the_t : NonNegativeInt
        The timepoint this plane is for. This is numbered from 0.
    the_z : NonNegativeInt
        The Z-section this plane is for. This is numbered from 0.
    annotation_ref : AnnotationRef, optional
    delta_t : float, optional
        Time since the beginning of the experiment. Units are set by
        DeltaTUnit.
    delta_t_unit : UnitsTime, optional
        The units of the DeltaT - default:seconds.
    exposure_time : float, optional
        The length of the exposure. Units are set by ExposureTimeUnit.
    exposure_time_unit : UnitsTime, optional
        The units of the ExposureTime - default:seconds.
    hash_sha1 : Hex40, optional
    position_x : float, optional
        The X position of the stage. Units are set by PositionXUnit.
    position_x_unit : UnitsLength, optional
        The units of the X stage position - default:.
    position_y : float, optional
        The Y position of the stage. Units are set by PositionYUnit.
    position_y_unit : UnitsLength, optional
        The units of the Y stage position - default:.
    position_z : float, optional
        The Z position of the stage. Units are set by PositionZUnit.
    position_z_unit : UnitsLength, optional
        The units of the Z stage position - default:.
    """

    the_c: NonNegativeInt
    the_t: NonNegativeInt
    the_z: NonNegativeInt
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    delta_t: Optional[float] = None
    delta_t_unit: Optional[UnitsTime] = UnitsTime("s")
    exposure_time: Optional[float] = None
    exposure_time_unit: Optional[UnitsTime] = UnitsTime("s")
    hash_sha1: Optional[Hex40] = None
    position_x: Optional[float] = None
    position_x_unit: Optional[UnitsLength] = UnitsLength("reference frame")
    position_y: Optional[float] = None
    position_y_unit: Optional[UnitsLength] = UnitsLength("reference frame")
    position_z: Optional[float] = None
    position_z_unit: Optional[UnitsLength] = UnitsLength("reference frame")
