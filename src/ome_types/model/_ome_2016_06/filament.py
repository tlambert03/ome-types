from enum import Enum
from typing import Literal, Optional

from ome_types._base_type import OMEType

from .light_source import LightSource


class Type(Enum):
    """The type of filament."""

    HALOGEN = "Halogen"
    INCANDESCENT = "Incandescent"
    OTHER = "Other"


class Filament(LightSource, OMEType):
    """The Filament element is used to describe various kinds of filament bulbs such
    as Incadescent or Halogen.

    The Power of the Filament is now stored in the LightSource.

    Parameters
    ----------
    id : LightSourceID
        A LightSource ID must be specified for each light source, and the
        individual light sources can be referred to by their LightSource IDs
        (eg from Channel).
    annotation_ref : AnnotationRef, optional
    lot_number : str, optional
        The lot number of the component.
    manufacturer : str, optional
        The manufacturer of the component.
    model : str, optional
        The Model of the component.
    power : float, optional
        The light-source power. Units are set by PowerUnit.
    power_unit : UnitsPower, optional
        The units of the Power - default:milliwatts.
    serial_number : str, optional
        The serial number of the component.
    type : Type, optional
        The type of filament.
    """

    kind: Literal["filament"] = "filament"
    type: Optional[Type] = None
