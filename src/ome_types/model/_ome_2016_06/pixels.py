from enum import Enum
from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .bin_data import BinData
from .channel import Channel
from .plane import Plane
from .simple_types import (
    PixelsID,
    PixelType,
    PositiveFloat,
    PositiveInt,
    UnitsLength,
    UnitsTime,
)
from .tiff_data import TiffData


class DimensionOrder(Enum):
    """The order in which the individual planes of data are interleaved."""

    XYCTZ = "XYCTZ"
    XYCZT = "XYCZT"
    XYTCZ = "XYTCZ"
    XYTZC = "XYTZC"
    XYZCT = "XYZCT"
    XYZTC = "XYZTC"


class Pixels(OMEType):
    """Pixels is going to be removed in the future, but it is still required.

    This is just notice that the contents of Pixels will be moved up to Image in a
    future release. This is because there has only been 1 Pixels object in each
    Image for some time. The concept of multiple Pixels sets for one Image failed
    to take off. It is therefore redundant.

    The Image will be unreadable if any of the required Pixel attributes are
    missing.

    The Pixels themselves can be stored within the OME-XML compressed by plane,
    and encoded in Base64. Or the Pixels may be stored in TIFF format.

    The Pixels element should contain a list of BinData or TiffData, each
    containing a single plane of pixels. These Pixels elements, when read in
    document order, must produce a 5-D pixel array of the size specified in this
    element, and in the dimension order specified by 'DimensionOrder'.

    All of the values in the Pixels object when present should match the same
    value stored in any associated TIFF format (e.g. SizeX should be the same).
    Where there is a mismatch our readers will take the value from the TIFF
    structure as overriding the value in the OME-XML. This is simply a pragmatic
    decision as it increases the likelihood of reading data from a slightly
    incorrect file.

    Parameters
    ----------
    dimension_order : DimensionOrder
        The order in which the individual planes of data are interleaved.
    id : PixelsID
    size_c : PositiveInt
        Dimensional size of pixel data array
    size_t : PositiveInt
        Dimensional size of pixel data array
    size_x : PositiveInt
        Dimensional size of pixel data array
    size_y : PositiveInt
        Dimensional size of pixel data array
    size_z : PositiveInt
        Dimensional size of pixel data array
    type : PixelType
        The variable type used to represent each pixel in the image.
    big_endian : bool, optional
        This is true if the pixels data was written in BigEndian order.  If
        this value is present it should match the value used in BinData or
        TiffData. If it does not a reader should honour the value used in the
        BinData or TiffData. This values is useful for MetadataOnly files and
        is to allow for future storage solutions.
    bin_data : BinData, optional
    channels : Channel, optional
    interleaved : bool, optional
        How the channels are arranged within the data block: true if channels
        are stored RGBRGBRGB...; false if channels are stored
        RRR...GGG...BBB...
    metadata_only : bool, optional
    physical_size_x : PositiveFloat, optional
        Physical size of a pixel. Units are set by PhysicalSizeXUnit.
    physical_size_x_unit : UnitsLength, optional
        The units of the physical size of a pixel - default:microns.
    physical_size_y : PositiveFloat, optional
        Physical size of a pixel. Units are set by PhysicalSizeYUnit.
    physical_size_y_unit : UnitsLength, optional
        The units of the physical size of a pixel - default:microns.
    physical_size_z : PositiveFloat, optional
        Physical size of a pixel. Units are set by PhysicalSizeZUnit.
    physical_size_z_unit : UnitsLength, optional
        The units of the physical size of a pixel - default:microns.
    planes : Plane, optional
    significant_bits : PositiveInt, optional
        The number of bits within the type storing each pixel that are
        significant. e.g. you can store 12 bit data within a 16 bit type. This
        does not reduce the storage requirements but can be a useful indicator
        when processing or viewing the image data.
    tiff_data_blocks : TiffData, optional
    time_increment : float, optional
        TimeIncrement is used for time series that have a global timing
        specification instead of per-timepoint timing info. For example in a
        video stream. Units are set by TimeIncrementUnit.
    time_increment_unit : UnitsTime, optional
        The units of the TimeIncrement - default:seconds.
    """

    dimension_order: DimensionOrder
    id: PixelsID
    size_c: PositiveInt
    size_t: PositiveInt
    size_x: PositiveInt
    size_y: PositiveInt
    size_z: PositiveInt
    type: PixelType
    big_endian: Optional[bool] = None
    bin_data: List[BinData] = Field(default_factory=list)
    channels: List[Channel] = Field(default_factory=list)
    interleaved: Optional[bool] = None
    metadata_only: bool = False
    physical_size_x: Optional[PositiveFloat] = None
    physical_size_x_unit: Optional[UnitsLength] = UnitsLength("µm")
    physical_size_y: Optional[PositiveFloat] = None
    physical_size_y_unit: Optional[UnitsLength] = UnitsLength("µm")
    physical_size_z: Optional[PositiveFloat] = None
    physical_size_z_unit: Optional[UnitsLength] = UnitsLength("µm")
    planes: List[Plane] = Field(default_factory=list)
    significant_bits: Optional[PositiveInt] = None
    tiff_data_blocks: List[TiffData] = Field(default_factory=list)
    time_increment: Optional[float] = None
    time_increment_unit: Optional[UnitsTime] = UnitsTime("s")
