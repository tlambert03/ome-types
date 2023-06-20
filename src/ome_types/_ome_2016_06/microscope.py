from enum import Enum
from typing import Optional

from ome_types._base_type import OMEType

from .manufacturer_spec import ManufacturerSpec


class Type(Enum):
    DISSECTION = "Dissection"
    ELECTROPHYSIOLOGY = "Electrophysiology"
    INVERTED = "Inverted"
    OTHER = "Other"
    UPRIGHT = "Upright"


class Microscope(ManufacturerSpec, OMEType):
    """The microscope's manufacturer specification.

    Parameters
    ----------
    lot_number : str, optional
        The lot number of the component.
    manufacturer : str, optional
        The manufacturer of the component.
    model : str, optional
        The Model of the component.
    serial_number : str, optional
        The serial number of the component.
    type : Type, optional
    """

    type: Optional[Type] = None
