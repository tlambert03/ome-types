from ome_types._base_type import OMEType

from .annotation import Annotation


class ListAnnotation(Annotation, OMEType):
    """This annotation is a grouping object.

    It uses the sequence of annotation refs from the base Annotation to form the
    list.

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
