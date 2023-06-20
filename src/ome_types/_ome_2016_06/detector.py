from enum import Enum
from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .manufacturer_spec import ManufacturerSpec
from .simple_types import DetectorID, UnitsElectricPotential


class Type(Enum):
    """The Type of detector.

    E.g. CCD, PMT, EMCCD etc.
    """

    ANALOG_VIDEO = "AnalogVideo"
    APD = "APD"
    CCD = "CCD"
    CMOS = "CMOS"
    CORRELATION_SPECTROSCOPY = "CorrelationSpectroscopy"
    EBCCD = "EBCCD"
    EMCCD = "EMCCD"
    FTIR = "FTIR"
    INTENSIFIED_CCD = "IntensifiedCCD"
    LIFETIME_IMAGING = "LifetimeImaging"
    OTHER = "Other"
    PHOTODIODE = "Photodiode"
    PMT = "PMT"
    SPECTROSCOPY = "Spectroscopy"


class Detector(ManufacturerSpec, OMEType):
    """The type of detector used to capture the image.

    The Detector ID can be used as a reference within the Channel element in the
    Image element. The values stored in Detector represent the fixed values,
    variable values modified during the acquisition go in DetectorSettings

    Each attribute now has an indication of what type of detector it applies to.
    This is preparatory work for cleaning up and possibly splitting this object
    into sub-types.

    Parameters
    ----------
    id : DetectorID
    amplification_gain : float, optional
        Gain applied to the detector signal. This is the electronic gain (as
        apposed to the inherent gain) that is set for the detector.
        {used:EMCCD#EMGain}
    annotation_ref : AnnotationRef, optional
    gain : float, optional
        The Detector Gain for this detector, as a float. {used:CCD,EMCCD,PMT}
    lot_number : str, optional
        The lot number of the component.
    manufacturer : str, optional
        The manufacturer of the component.
    model : str, optional
        The Model of the component.
    offset : float, optional
        The Detector Offset. {used:CCD,EMCCD}
    serial_number : str, optional
        The serial number of the component.
    type : Type, optional
        The Type of detector. E.g. CCD, PMT, EMCCD etc.
    voltage : float, optional
        The Voltage of the detector (e.g. PMT voltage) as a float. {used:PMT}
        Units are set by VoltageUnit.
    voltage_unit : UnitsElectricPotential, optional
        The units of the Voltage - default:volts.
    zoom : float, optional
        The fixed Zoom for a detector. {used:PMT}
    """

    id: DetectorID
    amplification_gain: Optional[float] = None
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    gain: Optional[float] = None
    offset: Optional[float] = None
    type: Optional[Type] = None
    voltage: Optional[float] = None
    voltage_unit: Optional[UnitsElectricPotential] = UnitsElectricPotential("V")
    zoom: Optional[float] = None
