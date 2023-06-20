from ome_types._base_type import OMEType

from .basic_annotation import BasicAnnotation


class NumericAnnotation(BasicAnnotation, OMEType):
    """An abstract Numeric Annotation from which some others are derived.

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
