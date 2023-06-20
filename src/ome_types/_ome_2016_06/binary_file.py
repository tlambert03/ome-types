from typing import Optional

from ome_types._base_type import OMEType

from .bin_data import BinData
from .external import External
from .simple_types import NonNegativeLong


class BinaryFile(OMEType):
    """Describes a binary file.

    Parameters
    ----------
    file_name : str
    size : NonNegativeLong
        Size of the uncompressed file.
    bin_data : BinData, optional
    external : External, optional
    mime_type : str, optional
    """

    file_name: str
    size: NonNegativeLong
    bin_data: Optional[BinData] = None
    external: Optional[External] = None
    mime_type: Optional[str] = None
