from typing import List

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .manufacturer_spec import ManufacturerSpec
from .simple_types import DichroicID


class Dichroic(ManufacturerSpec, OMEType):
    """The dichromatic beamsplitter or dichroic mirror used for this filter
    combination.

    Parameters
    ----------
    id : DichroicID
    annotation_ref : AnnotationRef, optional
    lot_number : str, optional
        The lot number of the component.
    manufacturer : str, optional
        The manufacturer of the component.
    model : str, optional
        The Model of the component.
    serial_number : str, optional
        The serial number of the component.
    """

    id: DichroicID
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
