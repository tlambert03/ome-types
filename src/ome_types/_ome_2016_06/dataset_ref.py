from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import DatasetID


class DatasetRef(Reference, OMEType):
    """The DatasetRef element refers to a Dataset by specifying the Dataset ID
    attribute.

    One or more DatasetRef elements may be listed within the Image element to
    specify what Datasets the Image belongs to.

    Parameters
    ----------
    id : DatasetID
    """

    id: DatasetID
