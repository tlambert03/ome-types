from typing import Optional

from pydantic import Field

from ome_types._autogenerated.ome_2016_06.units_length import UnitsLength
from ome_types._mixins._base_type import OMEType

__NAMESPACE__ = "http://www.openmicroscopy.org/Schemas/OME/2016-06"


class StageLabel(OMEType):
    """
    The StageLabel is used to specify a name and position for a stage position in
    the microscope's reference frame.

    Attributes
    ----------
    name : str
        (The StageLabel Name).
    x : None | float
        The X position of the stage label. Units are set by XUnit.
    x_unit : UnitsLength
        The units of the X stage position - default:[reference frame].
    y : None | float
        The Y position of the stage label. Units are set by YUnit.
    y_unit : UnitsLength
        The units of the Y stage position - default:[reference frame].
    z : None | float
        The Z position of the stage label. Units are set by ZUnit.
    z_unit : UnitsLength
        The units of the Z  stage position - default:[reference frame].
    """

    class Meta:
        namespace = "http://www.openmicroscopy.org/Schemas/OME/2016-06"

    name: str = Field(
        json_schema_extra={
            "name": "Name",
            "type": "Attribute",
            "required": True,
        }
    )
    x: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "name": "X",
            "type": "Attribute",
        },
    )
    x_unit: UnitsLength = Field(
        default=UnitsLength.REFERENCEFRAME,
        json_schema_extra={
            "name": "XUnit",
            "type": "Attribute",
        },
    )
    y: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "name": "Y",
            "type": "Attribute",
        },
    )
    y_unit: UnitsLength = Field(
        default=UnitsLength.REFERENCEFRAME,
        json_schema_extra={
            "name": "YUnit",
            "type": "Attribute",
        },
    )
    z: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "name": "Z",
            "type": "Attribute",
        },
    )
    z_unit: UnitsLength = Field(
        default=UnitsLength.REFERENCEFRAME,
        json_schema_extra={
            "name": "ZUnit",
            "type": "Attribute",
        },
    )