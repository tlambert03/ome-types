from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import ImageID


class ImageRef(Reference, OMEType):
    """The ImageRef element is a reference to an Image element.

    Parameters
    ----------
    id : ImageID
    """

    id: ImageID
