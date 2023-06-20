from typing import Optional

from ome_types._base_type import OMEType

from .boolean_annotation import BooleanAnnotation
from .comment_annotation import CommentAnnotation
from .double_annotation import DoubleAnnotation
from .file_annotation import FileAnnotation
from .list_annotation import ListAnnotation
from .long_annotation import LongAnnotation
from .map_annotation import MapAnnotation
from .tag_annotation import TagAnnotation
from .term_annotation import TermAnnotation
from .timestamp_annotation import TimestampAnnotation
from .xml_annotation import XMLAnnotation


class StructuredAnnotations(OMEType):
    """An unordered collection of annotation attached to objects in the OME data
    model.

    Parameters
    ----------
    boolean_annotations : BooleanAnnotation, optional
    comment_annotations : CommentAnnotation, optional
    double_annotations : DoubleAnnotation, optional
    file_annotations : FileAnnotation, optional
    list_annotations : ListAnnotation, optional
    long_annotations : LongAnnotation, optional
    map_annotations : MapAnnotation, optional
    tag_annotations : TagAnnotation, optional
    term_annotations : TermAnnotation, optional
    timestamp_annotations : TimestampAnnotation, optional
    xml_annotations : XMLAnnotation, optional
    """

    boolean_annotations: Optional[BooleanAnnotation] = None
    comment_annotations: Optional[CommentAnnotation] = None
    double_annotations: Optional[DoubleAnnotation] = None
    file_annotations: Optional[FileAnnotation] = None
    list_annotations: Optional[ListAnnotation] = None
    long_annotations: Optional[LongAnnotation] = None
    map_annotations: Optional[MapAnnotation] = None
    tag_annotations: Optional[TagAnnotation] = None
    term_annotations: Optional[TermAnnotation] = None
    timestamp_annotations: Optional[TimestampAnnotation] = None
    xml_annotations: Optional[XMLAnnotation] = None
