from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .dichroic_ref import DichroicRef
from .filter_ref import FilterRef


class LightPath(OMEType):
    """A description of the light path

    Parameters
    ----------
    annotation_ref : AnnotationRef, optional
    dichroic_ref : DichroicRef, optional
    emission_filter_ref : FilterRef, optional
        The Filters placed in the Emission light path.
    excitation_filter_ref : FilterRef, optional
        The Filters placed in the Excitation light path.
    """

    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    dichroic_ref: Optional[DichroicRef] = None
    emission_filter_ref: List[FilterRef] = Field(default_factory=list)
    excitation_filter_ref: List[FilterRef] = Field(default_factory=list)
