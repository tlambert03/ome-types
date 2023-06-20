from typing import Optional

from ome_types._base_type import OMEType

from .settings import Settings
from .simple_types import (
    Binning,
    DetectorID,
    PositiveInt,
    UnitsElectricPotential,
    UnitsFrequency,
)


class DetectorSettings(Settings, OMEType):
    """This holds the setting applied to a detector as well as a reference to the
    detector.

    The ID is the detector used in this case. The values stored in
    DetectorSettings represent the variable values, fixed values not modified
    during the acquisition go in Detector.

    Each attribute now has an indication of what type of detector it applies to.
    This is preparatory work for cleaning up and possibly splitting this object
    into sub-types.

    Parameters
    ----------
    id : DetectorID
    binning : Binning, optional
        Represents the number of pixels that are combined to form larger
        pixels. {used:CCD,EMCCD}
    gain : float, optional
        The Gain of the detector. {used:CCD,EMCCD,PMT}
    integration : PositiveInt, optional
        This is the number of sequential frames that get averaged, to improve
        the signal-to-noise ratio. {used:CCD,EMCCD}
    offset : float, optional
        The Offset of the detector. {used:CCD,EMCCD}
    read_out_rate : float, optional
        The speed at which the detector can count pixels.  {used:CCD,EMCCD}
        This is the bytes per second that can be read from the detector (like
        a baud rate). Units are set by ReadOutRateUnit.
    read_out_rate_unit : UnitsFrequency, optional
        The units of the ReadOutRate - default:megahertz.
    voltage : float, optional
        The Voltage of the detector. {used:PMT} Units are set by VoltageUnit.
    voltage_unit : UnitsElectricPotential, optional
        The units of the Voltage of the detector - default:volts
    zoom : float, optional
        The Zoom or "Confocal Zoom" or "Scan Zoom" for a detector. {used:PMT}
    """

    id: DetectorID
    binning: Optional[Binning] = None
    gain: Optional[float] = None
    integration: Optional[PositiveInt] = None
    offset: Optional[float] = None
    read_out_rate: Optional[float] = None
    read_out_rate_unit: Optional[UnitsFrequency] = UnitsFrequency("MHz")
    voltage: Optional[float] = None
    voltage_unit: Optional[UnitsElectricPotential] = UnitsElectricPotential("V")
    zoom: Optional[float] = None
