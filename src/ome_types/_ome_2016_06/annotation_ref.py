from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import AnnotationID


class AnnotationRef(Reference, OMEType):
    """The AnnotationRef element is a reference to an element derived from the
    CommonAnnotation element.

    Parameters
    ----------
    id : AnnotationID
    """

    id: AnnotationID
