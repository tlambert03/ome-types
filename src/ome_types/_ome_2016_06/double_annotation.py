from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .numeric_annotation import NumericAnnotation


class DoubleAnnotation(NumericAnnotation, OMEType):
    """A simple numerical annotation of type xsd:double

    Parameters
    ----------
    id : AnnotationID
    value : float
    annotation_ref : AnnotationRef, optional
    annotator : ExperimenterID, optional
        The Annotator is the person who attached this annotation. e.g. If
        UserA annotates something with TagB, owned by UserB, UserA is still
        the Annotator.
    description : str, optional
        A description for the annotation.
    namespace : str, optional
        We recommend the inclusion of a namespace for annotations you define.
        If it is absent then we assume the annotation is to use our (OME's)
        default interpretation for this type.
    """

    value: float
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    description: Optional[str] = None
