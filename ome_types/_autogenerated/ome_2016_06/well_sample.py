from datetime import datetime
from typing import Optional

from pydantic import Field

from ome_types._autogenerated.ome_2016_06.image_ref import ImageRef
from ome_types._autogenerated.ome_2016_06.units_length import UnitsLength
from ome_types._mixins._base_type import OMEType

__NAMESPACE__ = "http://www.openmicroscopy.org/Schemas/OME/2016-06"


class WellSample(OMEType):
    """
    WellSample is an individual image that has been captured within a Well.

    Attributes
    ----------
    image_ref : None | ImageRef
        This is the main link to the core Image element
    id : str
        (The WellSample ID).
    position_x : None | float
        The X position of the field (image) within the well relative to the well
        origin defined on the Plate. Units are set by PositionXUnit.
    position_x_unit : UnitsLength
        The units of the position in X - default:reference frame.
    position_y : None | float
        The Y position of the field (image) within the well relative to the well
        origin defined on the Plate. Units are set by PositionYUnit.
    position_y_unit : UnitsLength
        The units of the position in Y - default:reference frame.
    timepoint : None | datetime
        The time-point at which the image started to be collected
    index : int
        This records the order of the well samples. Each index should be unique for
        a given plate but they do not have to be sequential, there may be gaps if
        part of the dataset is missing. In the user interface the displayed value
        of the index will be calculated modulo the number of PlateAcquisitions for
        the plate.
    """

    class Meta:
        namespace = "http://www.openmicroscopy.org/Schemas/OME/2016-06"

    image_ref: Optional[ImageRef] = Field(
        default=None,
        json_schema_extra={
            "name": "ImageRef",
            "type": "Element",
        },
    )
    id: str = Field(
        default="__auto_sequence__",
        pattern=r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:WellSample:\S+)|(WellSample:\S+)",
        json_schema_extra={
            "name": "ID",
            "type": "Attribute",
            "required": True,
            "pattern": r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:WellSample:\S+)|(WellSample:\S+)",
        },
    )
    position_x: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "name": "PositionX",
            "type": "Attribute",
        },
    )
    position_x_unit: UnitsLength = Field(
        default=UnitsLength.REFERENCEFRAME,
        json_schema_extra={
            "name": "PositionXUnit",
            "type": "Attribute",
        },
    )
    position_y: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "name": "PositionY",
            "type": "Attribute",
        },
    )
    position_y_unit: UnitsLength = Field(
        default=UnitsLength.REFERENCEFRAME,
        json_schema_extra={
            "name": "PositionYUnit",
            "type": "Attribute",
        },
    )
    timepoint: Optional[datetime] = Field(
        default=None,
        json_schema_extra={
            "name": "Timepoint",
            "type": "Attribute",
        },
    )
    index: int = Field(
        ge=0,
        json_schema_extra={
            "name": "Index",
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        },
    )