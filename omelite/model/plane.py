from dataclasses import dataclass, field  # seems to be necessary for pyright
from datetime import timedelta
from typing import Optional

from pydantic.dataclasses import dataclass  # noqa
from pydantic import PositiveInt
from .units import UnitsLength, UnitsTime


@dataclass
class Plane:
    """The Plane object holds microscope stage and image timing data for a given
    channel/z-section/timepoint.
    """

    the_c: PositiveInt
    the_t: PositiveInt
    the_z: PositiveInt
    delta_t: Optional[timedelta] = None
    exposure_time: Optional[float] = field(default=None, metadata={"unit": UnitsTime})
    position_x: Optional[str] = field(default=None, metadata={"unit": UnitsLength})
    position_y: Optional[str] = field(default=None, metadata={"unit": UnitsLength})
    position_z: Optional[str] = field(default=None, metadata={"unit": UnitsLength})

    # delta_t_unit: Optional[str] = None
    # exposure_time_unit: Optional[str] = None
    # position_x_unit: Optional[str] = None
    # position_y_unit: Optional[str] = None
    # position_z_unit: Optional[str] = None
