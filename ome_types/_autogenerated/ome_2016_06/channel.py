from typing import Optional

from pydantic import Field

from ome_types._autogenerated.ome_2016_06.annotation_ref import AnnotationRef
from ome_types._autogenerated.ome_2016_06.channel_acquisition_mode import (
    Channel_AcquisitionMode,
)
from ome_types._autogenerated.ome_2016_06.channel_contrast_method import (
    Channel_ContrastMethod,
)
from ome_types._autogenerated.ome_2016_06.channel_illumination_type import (
    Channel_IlluminationType,
)
from ome_types._autogenerated.ome_2016_06.detector_settings import (
    DetectorSettings,
)
from ome_types._autogenerated.ome_2016_06.filter_set_ref import FilterSetRef
from ome_types._autogenerated.ome_2016_06.light_path import LightPath
from ome_types._autogenerated.ome_2016_06.light_source_settings import (
    LightSourceSettings,
)
from ome_types._autogenerated.ome_2016_06.units_length import UnitsLength
from ome_types._mixins._base_type import OMEType
from ome_types.model._color import Color

__NAMESPACE__ = "http://www.openmicroscopy.org/Schemas/OME/2016-06"


class Channel(OMEType):
    """There must be one per channel in the Image, even for a single-plane image.
    And information about how each of them was acquired is stored in the various
    optional *Ref elements.  Each Logical Channel is composed of one or more
    ChannelComponents.  For example, an entire spectrum in an FTIR experiment may
    be stored in a single Logical Channel with each discrete wavenumber of the
    spectrum.

    constituting a ChannelComponent of the FTIR Logical Channel.  An RGB image where the Red, Green and Blue components do not reflect discrete probes but are
    instead the output of a color camera would be treated similarly - one Logical channel with three ChannelComponents in this case.
    The total number of ChannelComponents for a set of pixels must equal SizeC.
    The IlluminationType attribute is a string enumeration which may be set to 'Transmitted', 'Epifluorescence', 'Oblique', or 'NonLinear'.
    The user interface logic for labeling a given channel for the user should use the first existing attribute in the following sequence:
    Name -&gt; Fluor -&gt; EmissionWavelength -&gt; ChannelComponent/Index.

    Attributes
    ----------
    light_source_settings : None | LightSourceSettings
        (The Channel LightSourceSettings).
    detector_settings : None | DetectorSettings
        (The Channel DetectorSettings).
    filter_set_ref : None | FilterSetRef
        (The Channel FilterSetRef).
    annotation_refs : list[AnnotationRef]
        (The Channel AnnotationRefs).
    light_path : None | LightPath
        (The Channel LightPath).
    id : str
        (The Channel ID).
    name : None | str
        A name for the channel that is suitable for presentation to the user.
    samples_per_pixel : None | int
        The number of samples the detector takes to form each pixel value.
        [units:none] Note: This is not the same as "Frame Averaging" - see
        Integration in DetectorSettings
    illumination_type : None | Channel_IlluminationType
        The method of illumination used to capture the channel.
    pinhole_size : None | float
        The optional PinholeSize attribute allows specifying adjustable pin hole
        diameters for confocal microscopes. Units are set by PinholeSizeUnit.
    pinhole_size_unit : UnitsLength
        The units of the pin hole diameter for confocal microscopes -
        default:microns[µm].
    acquisition_mode : None | Channel_AcquisitionMode
        AcquisitionMode describes the type of microscopy performed for each channel
    contrast_method : None | Channel_ContrastMethod
        ContrastMethod describes the technique used to achieve contrast for each
        channel
    excitation_wavelength : None | float
        Wavelength of excitation for a particular channel. Units are set by
        ExcitationWavelengthUnit.
    excitation_wavelength_unit : UnitsLength
        The units of the wavelength of excitation - default:nanometres[nm].
    emission_wavelength : None | float
        Wavelength of emission for a particular channel. Units are set by
        EmissionWavelengthUnit.
    emission_wavelength_unit : UnitsLength
        The units of the wavelength of emission - default:nanometres[nm].
    fluor : None | str
        The Fluor attribute is used for fluorescence images. This is the name of
        the fluorophore used to produce this channel [plain text string]
    nd_filter : None | float
        The NDfilter attribute is used to specify the combined effect of any
        neutral density filters used. The amount of light the filter transmits at a
        maximum [units:none] A fraction, as a value from 0.0 to 1.0. NOTE: This was
        formerly described as "units optical density expressed as a
        PercentFraction". This was how the field had been described in the schema
        from the beginning but all the use of it has been in the opposite
        direction, i.e. as a amount transmitted, not the amount blocked. This
        change has been made to make the model reflect this usage.
    pockel_cell_setting : None | int
        The PockelCellSetting used for this channel. This is the amount the
        polarization of the beam is rotated by. [units:none]
    color : Color
        A color used to render this channel - encoded as RGBA The default value
        "-1" is #FFFFFFFF so solid white (it is a signed 32 bit value) NOTE: Prior
        to the 2012-06 schema the default value was incorrect and produced a
        transparent red not solid white.
    """

    class Meta:
        namespace = "http://www.openmicroscopy.org/Schemas/OME/2016-06"

    light_source_settings: Optional[LightSourceSettings] = Field(
        default=None,
        json_schema_extra={
            "name": "LightSourceSettings",
            "type": "Element",
        },
    )
    detector_settings: Optional[DetectorSettings] = Field(
        default=None,
        json_schema_extra={
            "name": "DetectorSettings",
            "type": "Element",
        },
    )
    filter_set_ref: Optional[FilterSetRef] = Field(
        default=None,
        json_schema_extra={
            "name": "FilterSetRef",
            "type": "Element",
        },
    )
    annotation_refs: list[AnnotationRef] = Field(
        default_factory=list,
        json_schema_extra={
            "name": "AnnotationRef",
            "type": "Element",
        },
    )
    light_path: Optional[LightPath] = Field(
        default=None,
        json_schema_extra={
            "name": "LightPath",
            "type": "Element",
        },
    )
    id: str = Field(
        default="__auto_sequence__",
        pattern=r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Channel:\S+)|(Channel:\S+)",
        json_schema_extra={
            "name": "ID",
            "type": "Attribute",
            "required": True,
            "pattern": r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Channel:\S+)|(Channel:\S+)",
        },
    )
    name: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "name": "Name",
            "type": "Attribute",
        },
    )
    samples_per_pixel: Optional[int] = Field(
        default=None,
        ge=1,
        json_schema_extra={
            "name": "SamplesPerPixel",
            "type": "Attribute",
            "min_inclusive": 1,
        },
    )
    illumination_type: Optional[Channel_IlluminationType] = Field(
        default=None,
        json_schema_extra={
            "name": "IlluminationType",
            "type": "Attribute",
        },
    )
    pinhole_size: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "name": "PinholeSize",
            "type": "Attribute",
        },
    )
    pinhole_size_unit: UnitsLength = Field(
        default=UnitsLength.MICROMETER,
        json_schema_extra={
            "name": "PinholeSizeUnit",
            "type": "Attribute",
        },
    )
    acquisition_mode: Optional[Channel_AcquisitionMode] = Field(
        default=None,
        json_schema_extra={
            "name": "AcquisitionMode",
            "type": "Attribute",
        },
    )
    contrast_method: Optional[Channel_ContrastMethod] = Field(
        default=None,
        json_schema_extra={
            "name": "ContrastMethod",
            "type": "Attribute",
        },
    )
    excitation_wavelength: Optional[float] = Field(
        default=None,
        gt=0.0,
        json_schema_extra={
            "name": "ExcitationWavelength",
            "type": "Attribute",
            "min_exclusive": 0.0,
        },
    )
    excitation_wavelength_unit: UnitsLength = Field(
        default=UnitsLength.NANOMETER,
        json_schema_extra={
            "name": "ExcitationWavelengthUnit",
            "type": "Attribute",
        },
    )
    emission_wavelength: Optional[float] = Field(
        default=None,
        gt=0.0,
        json_schema_extra={
            "name": "EmissionWavelength",
            "type": "Attribute",
            "min_exclusive": 0.0,
        },
    )
    emission_wavelength_unit: UnitsLength = Field(
        default=UnitsLength.NANOMETER,
        json_schema_extra={
            "name": "EmissionWavelengthUnit",
            "type": "Attribute",
        },
    )
    fluor: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "name": "Fluor",
            "type": "Attribute",
        },
    )
    nd_filter: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "name": "NDFilter",
            "type": "Attribute",
        },
    )
    pockel_cell_setting: Optional[int] = Field(
        default=None,
        json_schema_extra={
            "name": "PockelCellSetting",
            "type": "Attribute",
        },
    )
    color: Color = Field(
        default_factory=Color,
        json_schema_extra={
            "name": "Color",
            "type": "Attribute",
        },
    )


AcquisitionMode = Channel_AcquisitionMode
ContrastMethod = Channel_ContrastMethod
IlluminationType = Channel_IlluminationType
