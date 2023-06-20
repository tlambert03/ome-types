from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import FolderID


class FolderRef(Reference, OMEType):
    """The FolderRef element refers to a Folder by specifying the Folder ID
    attribute.

    One or more FolderRef elements may be listed within the Folder element to
    specify what Folders the Folder contains. This tree hierarchy must be acyclic.

    Parameters
    ----------
    id : FolderID
    """

    id: FolderID
