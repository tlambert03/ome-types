from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .dichroic_ref import DichroicRef
from .filter_ref import FilterRef
from .manufacturer_spec import ManufacturerSpec
from .simple_types import FilterSetID


class FilterSet(ManufacturerSpec, OMEType):
    """Filter set manufacturer specification

    Parameters
    ----------
    id : FilterSetID
    dichroic_ref : DichroicRef, optional
    emission_filter_ref : FilterRef, optional
        The Filters placed in the Emission light path.
    excitation_filter_ref : FilterRef, optional
        The Filters placed in the Excitation light path.
    lot_number : str, optional
        The lot number of the component.
    manufacturer : str, optional
        The manufacturer of the component.
    model : str, optional
        The Model of the component.
    serial_number : str, optional
        The serial number of the component.
    """

    id: FilterSetID
    dichroic_ref: Optional[DichroicRef] = None
    emission_filter_ref: List[FilterRef] = Field(default_factory=list)
    excitation_filter_ref: List[FilterRef] = Field(default_factory=list)
