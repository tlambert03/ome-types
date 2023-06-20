from ome_types._base_type import OMEType

from .annotation import Annotation


class TypeAnnotation(Annotation, OMEType):
    """An abstract Type Annotation from which some others are derived.

    Parameters
    ----------
    id : AnnotationID
    annotator : ExperimenterID, optional
        The Annotator is the person who attached this annotation. e.g. If
        UserA annotates something with TagB, owned by UserB, UserA is still
        the Annotator.
    namespace : str, optional
        We recommend the inclusion of a namespace for annotations you define.
        If it is absent then we assume the annotation is to use our (OME's)
        default interpretation for this type.
    """
