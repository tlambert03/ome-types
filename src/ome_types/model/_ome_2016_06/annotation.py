from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .simple_types import AnnotationID, ExperimenterID


class Annotation(OMEType):
    """An annotation from which all others are ultimately derived.

    Parameters
    ----------
    id : AnnotationID
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

    id: AnnotationID
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    annotator: Optional[ExperimenterID] = None
    description: Optional[str] = None
    namespace: Optional[str] = None
