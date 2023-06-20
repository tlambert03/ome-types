from enum import Enum
from typing import Optional

from ome_types._base_type import OMEType


class Compression(Enum):
    """Specifies the compression scheme used to encode the data."""

    BZIP2 = "bzip2"
    NONE = "none"
    ZLIB = "zlib"


class BinData(OMEType):
    """The contents of this element are base64-encoded.

    These are not CDATA sections, just a base64 stream.

    Parameters
    ----------
    big_endian : bool
        This is true if the binary data was written in BigEndian order. This
        is dependent on the system architecture of the machine that wrote the
        pixels. True for essentially all modern CPUs other than Intel and
        Alpha. All Binary data must be written in the same endian order.
    length : int
        Character count attribute for the BinData field. This is the length of
        the base-64 encoded block. It allows easy skipping of the block when
        parsing the file.
    compression : Compression, optional
        Specifies the compression scheme used to encode the data.
    """

    value: str
    big_endian: bool
    length: int
    compression: Optional[Compression] = Compression("none")
