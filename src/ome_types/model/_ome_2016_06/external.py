from enum import Enum
from typing import Optional

from ome_types._base_type import OMEType

from .simple_types import Hex40


class Compression(Enum):
    """Specifies the compression scheme used to encode the data."""

    BZIP2 = "bzip2"
    NONE = "none"
    ZLIB = "zlib"


class External(OMEType):
    """Describes a file location.

    Can optionally specify a portion of a file using Offset and a ReadLength.
    If Offset and ReadLength are specified in conjuction with Compression, then
    they point into the uncompressed file.

    Parameters
    ----------
    href : str
        file location
    sha1 : Hex40
        The digest of the file specified in href.
    compression : Compression, optional
        Specifies the compression scheme used to encode the data.
    """

    href: str
    sha1: Hex40
    compression: Optional[Compression] = Compression("none")
