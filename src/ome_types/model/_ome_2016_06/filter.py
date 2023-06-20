from enum import Enum
from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .manufacturer_spec import ManufacturerSpec
from .simple_types import FilterID
from .transmittance_range import TransmittanceRange


class Type(Enum):
    BAND_PASS = "BandPass"
    DICHROIC = "Dichroic"
    LONG_PASS = "LongPass"
    MULTI_PASS = "MultiPass"
    NEUTRAL_DENSITY = "NeutralDensity"
    OTHER = "Other"
    SHORT_PASS = "ShortPass"
    TUNEABLE = "Tuneable"


class Filter(ManufacturerSpec, OMEType):
    """A filter is either an excitation or emission filters.

    There should be one filter element specified per wavelength in the image. The
    channel number associated with a filter set is specified in Channel. It is
    based on the FilterSpec type, so has the required attributes Manufacturer,
    Model, and LotNumber. It may also contain a Type attribute which may be set to
    'LongPass', 'ShortPass', 'BandPass', 'MultiPass', 'Dichroic',
    'NeutralDensity', 'Tuneable' or 'Other'. It can be associated with an optional
    FilterWheel - Note: this is not the same as a FilterSet

    Parameters
    ----------
    id : FilterID
    annotation_ref : AnnotationRef, optional
    filter_wheel : str, optional
        A filter 'wheel' in OME can refer to any arrangement of filters in a
        filter holder of any shape. It could, for example, be a filter slider.
        [plain text string]
    lot_number : str, optional
        The lot number of the component.
    manufacturer : str, optional
        The manufacturer of the component.
    model : str, optional
        The Model of the component.
    serial_number : str, optional
        The serial number of the component.
    transmittance_range : TransmittanceRange, optional
    type : Type, optional
    """

    id: FilterID
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    filter_wheel: Optional[str] = None
    transmittance_range: Optional[TransmittanceRange] = None
    type: Optional[Type] = None
