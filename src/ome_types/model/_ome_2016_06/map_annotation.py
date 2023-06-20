from ome_types._base_type import OMEType

from .annotation import Annotation
from .map import Map


class MapAnnotation(Annotation, OMEType):
    """An map annotation.

    The contents of this is a list of key/value pairs.

    Parameters
    ----------
    id : AnnotationID
    value : Map
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

    value: Map
