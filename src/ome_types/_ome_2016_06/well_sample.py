from datetime import datetime
from typing import Optional

from ome_types._base_type import OMEType

from .image_ref import ImageRef
from .simple_types import NonNegativeInt, UnitsLength, WellSampleID


class WellSample(OMEType):
    """WellSample is an individual image that has been captured within a Well.

    Parameters
    ----------
    id : WellSampleID
    index : NonNegativeInt
        This records the order of the well samples. Each index should be
        unique for a given plate but they do not have to be sequential, there
        may be gaps if part of the dataset is missing. In the user interface
        the displayed value of the index will be calculated modulo the number
        of PlateAcquisitions for the plate.
    image_ref : ImageRef, optional
        This is the main link to the core Image element
    position_x : float, optional
        The X position of the field (image) within the well relative to the
        well origin defined on the Plate. Units are set by PositionXUnit.
    position_x_unit : UnitsLength, optional
        The units of the position in X - default:reference frame.
    position_y : float, optional
        The Y position of the field (image) within the well relative to the
        well origin defined on the Plate. Units are set by PositionYUnit.
    position_y_unit : UnitsLength, optional
        The units of the position in Y - default:reference frame.
    timepoint : datetime, optional
        The time-point at which the image started to be collected
    """

    id: WellSampleID
    index: NonNegativeInt
    image_ref: Optional[ImageRef] = None
    position_x: Optional[float] = None
    position_x_unit: Optional[UnitsLength] = UnitsLength("reference frame")
    position_y: Optional[float] = None
    position_y_unit: Optional[UnitsLength] = UnitsLength("reference frame")
    timepoint: Optional[datetime] = None
