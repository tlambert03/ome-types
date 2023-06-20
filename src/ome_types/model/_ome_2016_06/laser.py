from enum import Enum
from typing import Optional

from typing_extensions import Literal

from ome_types._base_type import OMEType

from .light_source import LightSource
from .pump import Pump
from .simple_types import PositiveFloat, PositiveInt, UnitsFrequency, UnitsLength


class Type(Enum):
    """Type is the general category of laser."""

    DYE = "Dye"
    EXCIMER = "Excimer"
    FREE_ELECTRON = "FreeElectron"
    GAS = "Gas"
    METAL_VAPOR = "MetalVapor"
    OTHER = "Other"
    SEMICONDUCTOR = "Semiconductor"
    SOLID_STATE = "SolidState"


class LaserMedium(Enum):
    """The Medium attribute specifies the actual lasing medium for a given laser
    type.
    """

    AG = "Ag"
    ALEXANDRITE = "Alexandrite"
    AR = "Ar"
    AR_CL = "ArCl"
    AR_FL = "ArFl"
    CO = "CO"
    CO2 = "CO2"
    COUMARIN_C30 = "CoumarinC30"
    CU = "Cu"
    E_MINUS = "EMinus"
    ER_GLASS = "ErGlass"
    ER_YAG = "ErYAG"
    GA_AL_AS = "GaAlAs"
    GA_AS = "GaAs"
    H2_O = "H2O"
    H_FL = "HFl"
    HE_CD = "HeCd"
    HE_NE = "HeNe"
    HO_YAG = "HoYAG"
    HO_YLF = "HoYLF"
    KR = "Kr"
    KR_CL = "KrCl"
    KR_FL = "KrFl"
    N = "N"
    ND_GLASS = "NdGlass"
    ND_YAG = "NdYAG"
    OTHER = "Other"
    RHODAMINE6_G = "Rhodamine6G"
    RUBY = "Ruby"
    TI_SAPPHIRE = "TiSapphire"
    XE = "Xe"
    XE_BR = "XeBr"
    XE_CL = "XeCl"
    XE_FL = "XeFl"


class Pulse(Enum):
    """The Pulse mode of the laser."""

    CW = "CW"
    MODE_LOCKED = "ModeLocked"
    OTHER = "Other"
    Q_SWITCHED = "QSwitched"
    REPETITIVE = "Repetitive"
    SINGLE = "Single"


class Laser(LightSource, OMEType):
    """Laser types are specified using two attributes - the Type and the LaserMedium.

    Parameters
    ----------
    id : LightSourceID
        A LightSource ID must be specified for each light source, and the
        individual light sources can be referred to by their LightSource IDs
        (eg from Channel).
    annotation_ref : AnnotationRef, optional
    frequency_multiplication : PositiveInt, optional
        FrequencyMultiplication that may be specified.
    laser_medium : LaserMedium, optional
        The Medium attribute specifies the actual lasing medium for a given
        laser type.
    lot_number : str, optional
        The lot number of the component.
    manufacturer : str, optional
        The manufacturer of the component.
    model : str, optional
        The Model of the component.
    pockel_cell : bool, optional
        If true the laser has a PockelCell to rotate the polarization of the
        beam.
    power : float, optional
        The light-source power. Units are set by PowerUnit.
    power_unit : UnitsPower, optional
        The units of the Power - default:milliwatts.
    pulse : Pulse, optional
        The Pulse mode of the laser.
    pump : Pump, optional
        The Laser element may contain a Pump sub-element which refers to a
        LightSource used as a laser pump.
    repetition_rate : float, optional
        The is the rate in Hz at which the laser pulses if the Pulse type is
        'Repetitive'. hertz Units are set by RepetitionRateUnit.
    repetition_rate_unit : UnitsFrequency, optional
        The units of the RepetitionRate - default:hertz.
    serial_number : str, optional
        The serial number of the component.
    tuneable : bool, optional
        Whether or not the laser is Tuneable
    type : Type, optional
        Type is the general category of laser.
    wavelength : PositiveFloat, optional
        The Wavelength of the laser. Units are set by WavelengthUnit.
    wavelength_unit : UnitsLength, optional
        The units of the Wavelength - default:nanometres.
    """

    kind: Literal["laser"] = "laser"
    frequency_multiplication: Optional[PositiveInt] = None
    laser_medium: Optional[LaserMedium] = None
    pockel_cell: Optional[bool] = None
    pulse: Optional[Pulse] = None
    pump: Optional[Pump] = None
    repetition_rate: Optional[float] = None
    repetition_rate_unit: Optional[UnitsFrequency] = UnitsFrequency("Hz")
    tuneable: Optional[bool] = None
    type: Optional[Type] = None
    wavelength: Optional[PositiveFloat] = None
    wavelength_unit: Optional[UnitsLength] = UnitsLength("nm")
