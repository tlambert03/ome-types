from enum import Enum
from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .detector_settings import DetectorSettings
from .filter_set_ref import FilterSetRef
from .light_path import LightPath
from .light_source_settings import LightSourceSettings
from .simple_types import ChannelID, Color, PositiveFloat, PositiveInt, UnitsLength


class IlluminationType(Enum):
    """The method of illumination used to capture the channel."""

    EPIFLUORESCENCE = "Epifluorescence"
    NON_LINEAR = "NonLinear"
    OBLIQUE = "Oblique"
    OTHER = "Other"
    TRANSMITTED = "Transmitted"


class AcquisitionMode(Enum):
    """AcquisitionMode describes the type of microscopy performed for each channel."""

    BRIGHT_FIELD = "BrightField"
    FLUORESCENCE_CORRELATION_SPECTROSCOPY = "FluorescenceCorrelationSpectroscopy"
    FLUORESCENCE_LIFETIME = "FluorescenceLifetime"
    FSM = "FSM"
    LASER_SCANNING_CONFOCAL_MICROSCOPY = "LaserScanningConfocalMicroscopy"
    LCM = "LCM"
    MULTI_PHOTON_MICROSCOPY = "MultiPhotonMicroscopy"
    NEAR_FIELD_SCANNING_OPTICAL_MICROSCOPY = "NearFieldScanningOpticalMicroscopy"
    OTHER = "Other"
    PALM = "PALM"
    SECOND_HARMONIC_GENERATION_IMAGING = "SecondHarmonicGenerationImaging"
    SINGLE_MOLECULE_IMAGING = "SingleMoleculeImaging"
    SLIT_SCAN_CONFOCAL = "SlitScanConfocal"
    SPECTRAL_IMAGING = "SpectralImaging"
    SPIM = "SPIM"
    SPINNING_DISK_CONFOCAL = "SpinningDiskConfocal"
    STED = "STED"
    STORM = "STORM"
    STRUCTURED_ILLUMINATION = "StructuredIllumination"
    SWEPT_FIELD_CONFOCAL = "SweptFieldConfocal"
    TIRF = "TIRF"
    TOTAL_INTERNAL_REFLECTION = "TotalInternalReflection"
    WIDE_FIELD = "WideField"


class ContrastMethod(Enum):
    """ContrastMethod describes the technique used to achieve contrast for each
    channel.
    """

    BRIGHTFIELD = "Brightfield"
    DARKFIELD = "Darkfield"
    DIC = "DIC"
    FLUORESCENCE = "Fluorescence"
    HOFFMAN_MODULATION = "HoffmanModulation"
    OBLIQUE_ILLUMINATION = "ObliqueIllumination"
    OTHER = "Other"
    PHASE = "Phase"
    POLARIZED_LIGHT = "PolarizedLight"


class Channel(OMEType):
    """There must be one per channel in the Image, even for a single-plane image.

    And information about how each of them was acquired is stored in the various
    optional `*Ref` elements.  Each Logical Channel is composed of one or more
    ChannelComponents.  For example, an entire spectrum in an FTIR experiment may
    be stored in a single Logical Channel with each discrete wavenumber of the
    spectrum constituting a ChannelComponent of the FTIR Logical Channel.  An RGB
    image where the Red, Green and Blue components do not reflect discrete probes
    but are instead the output of a color camera would be treated similarly - one
    Logical channel with three ChannelComponents in this case. The total number of
    ChannelComponents for a set of pixels must equal SizeC. The IlluminationType
    attribute is a string enumeration which may be set to 'Transmitted',
    'Epifluorescence', 'Oblique', or 'NonLinear'. The user interface logic for
    labeling a given channel for the user should use the first existing attribute
    in the following sequence: Name -> Fluor -> EmissionWavelength ->
    ChannelComponent/Index.

    Parameters
    ----------
    id : ChannelID
    acquisition_mode : AcquisitionMode, optional
        AcquisitionMode describes the type of microscopy performed for each
        channel
    annotation_ref : AnnotationRef, optional
    color : Color, optional
        A color used to render this channel - encoded as RGBA The default
        value "-1" is #FFFFFFFF so solid white (it is a signed 32 bit value)
        NOTE: Prior to the 2012-06 schema the default value was incorrect and
        produced a transparent red not solid white.
    contrast_method : ContrastMethod, optional
        ContrastMethod describes the technique used to achieve contrast for
        each channel
    detector_settings : DetectorSettings, optional
    emission_wavelength : PositiveFloat, optional
        Wavelength of emission for a particular channel. Units are set by
        EmissionWavelengthUnit.
    emission_wavelength_unit : UnitsLength, optional
        The units of the wavelength of emission - default:nanometres.
    excitation_wavelength : PositiveFloat, optional
        Wavelength of excitation for a particular channel. Units are set by
        ExcitationWavelengthUnit.
    excitation_wavelength_unit : UnitsLength, optional
        The units of the wavelength of excitation - default:nanometres.
    filter_set_ref : FilterSetRef, optional
    fluor : str, optional
        The Fluor attribute is used for fluorescence images. This is the name
        of the fluorophore used to produce this channel
    illumination_type : IlluminationType, optional
        The method of illumination used to capture the channel.
    light_path : LightPath, optional
    light_source_settings : LightSourceSettings, optional
    name : str, optional
        A name for the channel that is suitable for presentation to the user.
    nd_filter : float, optional
        The NDfilter attribute is used to specify the combined effect of any
        neutral density filters used. The amount of light the filter transmits
        at a maximum A fraction, as a value from 0.0 to 1.0.  NOTE: This was
        formerly described as "units optical density expressed as a
        PercentFraction". This was how the field had been described in the
        schema from the beginning but all the use of it has been in the
        opposite direction, i.e. as a amount transmitted, not the amount
        blocked. This change has been made to make the model reflect this
        usage.
    pinhole_size : float, optional
        The optional PinholeSize attribute allows specifying adjustable pin
        hole diameters for confocal microscopes. Units are set by
        PinholeSizeUnit.
    pinhole_size_unit : UnitsLength, optional
        The units of the pin hole diameter for confocal microscopes -
        default:microns.
    pockel_cell_setting : int, optional
        The PockelCellSetting used for this channel. This is the amount the
        polarization of the beam is rotated by.
    samples_per_pixel : PositiveInt, optional
        The number of samples the detector takes to form each pixel value.
        Note: This is not the same as "Frame Averaging" - see Integration in
        DetectorSettings
    """

    id: ChannelID
    acquisition_mode: Optional[AcquisitionMode] = None
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    color: Optional[Color] = Color("white")
    contrast_method: Optional[ContrastMethod] = None
    detector_settings: Optional[DetectorSettings] = None
    emission_wavelength: Optional[PositiveFloat] = None
    emission_wavelength_unit: Optional[UnitsLength] = UnitsLength("nm")
    excitation_wavelength: Optional[PositiveFloat] = None
    excitation_wavelength_unit: Optional[UnitsLength] = UnitsLength("nm")
    filter_set_ref: Optional[FilterSetRef] = None
    fluor: Optional[str] = None
    illumination_type: Optional[IlluminationType] = None
    light_path: Optional[LightPath] = None
    light_source_settings: Optional[LightSourceSettings] = None
    name: Optional[str] = None
    nd_filter: Optional[float] = None
    pinhole_size: Optional[float] = None
    pinhole_size_unit: Optional[UnitsLength] = UnitsLength("µm")
    pockel_cell_setting: Optional[int] = None
    samples_per_pixel: Optional[PositiveInt] = None
