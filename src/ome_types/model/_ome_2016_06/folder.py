from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .folder_ref import FolderRef
from .image_ref import ImageRef
from .roi_ref import ROIRef
from .simple_types import FolderID


class Folder(OMEType):
    """An element specifying a possibly heterogeneous collection of data.

    Folders may contain Folders so that data may be organized within a tree of
    Folders. Data may be in multiple Folders but a Folder may not be in more than
    one other Folder.

    Parameters
    ----------
    id : FolderID
    annotation_ref : AnnotationRef, optional
    description : str, optional
        A description for the folder.
    folder_ref : FolderRef, optional
    image_ref : ImageRef, optional
    name : str, optional
        A name for the folder that is suitable for presentation to the user.
    roi_ref : ROIRef, optional
    """

    id: FolderID
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    description: Optional[str] = None
    folder_ref: List[FolderRef] = Field(default_factory=list)
    image_ref: List[ImageRef] = Field(default_factory=list)
    name: Optional[str] = None
    roi_ref: List[ROIRef] = Field(default_factory=list)
