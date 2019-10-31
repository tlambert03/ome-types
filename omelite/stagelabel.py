from dataclasses import field, dataclass  # seems to be necessary for pyright
from pydantic.dataclasses import dataclass  # noqa
from .units import UnitsLength
from typing import Optional


@dataclass
class StageLabel:
    """ The StageLabel is used to specify a name and position for a stage position in the
    microscope's reference frame.
    """

    name: str
    x: Optional[float] = field(default=None, metadata={"unit": UnitsLength.um})
    y: Optional[float] = field(default=None, metadata={"unit": UnitsLength.um})
    z: Optional[float] = field(default=None, metadata={"unit": UnitsLength.um})
