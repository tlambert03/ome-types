from typing import Optional

from ome_types._base_type import OMEType

from .simple_types import UnitsLength


class StageLabel(OMEType):
    """The StageLabel is used to specify a name and position for a stage position in
    the microscope's reference frame.

    Parameters
    ----------
    name : str
    x : float, optional
        The X position of the stage label. Units are set by XUnit.
    x_unit : UnitsLength, optional
        The units of the X stage position - default:.
    y : float, optional
        The Y position of the stage label. Units are set by YUnit.
    y_unit : UnitsLength, optional
        The units of the Y stage position - default:.
    z : float, optional
        The Z position of the stage label. Units are set by ZUnit.
    z_unit : UnitsLength, optional
        The units of the Z  stage position - default:.
    """

    name: str
    x: Optional[float] = None
    x_unit: Optional[UnitsLength] = UnitsLength("reference frame")
    y: Optional[float] = None
    y_unit: Optional[UnitsLength] = UnitsLength("reference frame")
    z: Optional[float] = None
    z_unit: Optional[UnitsLength] = UnitsLength("reference frame")
