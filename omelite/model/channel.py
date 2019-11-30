from dataclasses import dataclass, field  # seems to be necessary for pyright
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic.dataclasses import dataclass  # noqa
from pydantic import PositiveFloat

from omelite.units import UnitsLength


class AquisitionMode(Enum):
    """AcquisitionMode describes the type of microscopy performed for each channel"""

    wide_field = "WideField"
    laser_scanning_confocal_microscopy = "LaserScanningConfocalMicroscopy"
    spinning_disk_confocal = "SpinningDiskConfocal"
    slit_scan_confocal = "SlitScanConfocal"
    multi_photon_microscopy = "MultiPhotonMicroscopy"
    structured_illumination = "StructuredIllumination"
    single_molecule_imaging = "SingleMoleculeImaging"
    total_internal_reflection = "TotalInternalReflection"
    fluorescence_lifetime = "FluorescenceLifetime"
    spectral_imaging = "SpectralImaging"
    fluorescence_correlation_spectroscopy = "FluorescenceCorrelationSpectroscopy"
    near_field_scanning_optical_microscopy = "NearFieldScanningOpticalMicroscopy"
    second_harmonic_generation_imaging = "SecondHarmonicGenerationImaging"
    palm = "PALM"
    storm = "STORM"
    sted = "STED"
    tirf = "TIRF"
    fsm = "FSM"
    lcm = "LCM"
    other = "Other"
    bright_field = "BrightField"
    swept_field_confocal = "SweptFieldConfocal"
    spim = "SPIM"


class ContrastMethod(Enum):
    """ContrastMethod describes the technique used to achieve contrast for each channel"""

    brightfield = "Brightfield"
    phase = "Phase"
    dic = "DIC"
    hoffman_modulation = "HoffmanModulation"
    oblique_illumination = "ObliqueIllumination"
    polarized_light = "PolarizedLight"
    darkfield = "Darkfield"
    fluorescence = "Fluorescence"
    other = "Other"


@dataclass
class Channel:
    """There must be one per channel in the Image, even for a single-plane image. 
    And information about how each of them was acquired is stored in the various optional
    *Ref elements.  Each Logical Channel is composed of one or more ChannelComponents.  For
    example, an entire spectrum in an FTIR experiment may be stored in a single Logical
    Channel with each discrete wavenumber of the spectrum constituting a ChannelComponent of
    the FTIR Logical Channel.  An RGB image where the Red, Green and Blue components do not
    reflect discrete probes but are instead the output of a color camera would be treated
    similarly - one Logical channel with three ChannelComponents in this case. The total
    number of ChannelComponents for a set of pixels must equal SizeC. The IlluminationType
    attribute is a string enumeration which may be set to 'Transmitted', 'Epifluorescence',
    'Oblique', or 'NonLinear'. The user interface logic for labeling a given channel for the
    user should use the first existing attribute in the following sequence: Name -> Fluor ->
    EmissionWavelength -> ChannelComponent/Index.
    """

    acquisition_mode: Optional[AquisitionMode] = None
    contrast_method: Optional[ContrastMethod] = None
    emission_wavelength: Optional[PositiveFloat] = None
    excitation_wavelength: Optional[PositiveFloat] = None
    fluor: Optional[str] = None  # could be FPbase UUID
    name: Optional[str] = None
    pinhole_size: Optional[float] = field(
        default=None, metadata={"unit": UnitsLength.um}
    )
    # light_source_settings: Optional[LightSourceSettings] = None
    # detector_settings: Optional[DetectorSettings] = None
    # filter_set: Optional[FilterSet] = None
    # light_path: Optional[LightPath] = None
    # annotations: List[Annotation] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4, init=False, repr=False)

    # # UNUSED
    # color
    # pockel_cell_setting: Optional[float] = None
    # nd_filter: Optional[float] = None
    # emission_wavelength_unit
    # excitation_wavelength_unit
    # pinhole_size_unit
    # samples_per_pixel: Optional[PositiveInt] = None
