from dataclasses import dataclass, field  # seems to be necessary for pyright
from datetime import datetime, timedelta
from typing import List, Optional, Union
from uuid import UUID, uuid4
from numpy import ndarray

from pydantic.dataclasses import dataclass  # noqa
from .channel import Channel
from .plane import Plane
from .experimenter import Experimenter
from .stagelabel import StageLabel
from .units import DimensionOrder, PixelType, UnitsLength
from pydantic import PositiveInt, PositiveFloat, ConstrainedInt


class NonNegativeInt(ConstrainedInt):
    ge = 0


@dataclass
class Pixels:
    """Pixels is going to be removed in the future, but it is still required.

    This is just notice that the contents of Pixels will be moved up to Image in a future
    release. This is because there has only been 1 Pixels object in each Image for some
    time. The concept of multiple Pixels sets for one Image failed to take off. It is
    therefore redundant.

    The Image will be unreadable if any of the required Pixel attributes are missing.

    The Pixels themselves can be stored within the OME-XML compressed by plane, and encoded
    in Base64. Or the Pixels may be stored in TIFF format.

    The Pixels element should contain a list of BinData or TiffData, each containing a
    single plane of pixels. These Pixels elements, when read in document order, must produce
    a 5-D pixel array of the size specified in this element, and in the dimension order
    specified by 'DimensionOrder'.

    All of the values in the Pixels object when present should match the same value stored
    in any associated TIFF format (e.g. SizeX should be the same). Where there is a mismatch
    our readers will take the value from the TIFF structure as overriding the value in the
    OME-XML. This is simply a pragmatic decision as it increases the likelihood of reading
    data from a slightly incorrect file.
    """

    size_c: PositiveInt
    size_t: PositiveInt
    size_x: PositiveInt
    size_y: PositiveInt
    size_z: PositiveInt
    dimension_order: DimensionOrder
    type: PixelType
    # the data can either be a numpy array or a string to a tiff file
    data: Optional[Union[ndarray, str]] = None  # None = MetadataOnly
    physical_size_x: Optional[PositiveFloat] = field(
        default=None, metadata={"unit": UnitsLength.um}
    )
    physical_size_y: Optional[PositiveFloat] = field(
        default=None, metadata={"unit": UnitsLength.um}
    )
    physical_size_z: Optional[PositiveFloat] = field(
        default=None, metadata={"unit": UnitsLength.um}
    )
    interleaved: Optional[bool] = False
    time_increment: Optional[timedelta] = None
    channels: List[Channel] = field(default_factory=list)
    planes: List[Plane] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4, init=False, repr=False)

    # # UNUSED
    # big_endian
    # significant_bits


@dataclass
class Image(Pixels):
    """This element describes the actual image and its meta-data.

    The elements that are references (ending in Ref or Settings) refer to elements defined
    outside of the Image element. Ref elements are simple links, while Settings elements are
    links with additional values.

    If any of the required Image attributes or elements are missing, its guaranteed to be an
    invalid document. The required attributes and elements are ID and Pixels.

    ExperimenterRef is required for all Images with well formed LSIDs. ImageType is a
    vendor-specific designation of the type of image this is. Examples of ImageType include
    'STK', 'SoftWorx', etc. The Name attributes are in all cases the name of the element
    instance. In this case, the name of the image, not necessarily the filename. Physical
    size of pixels are microns[µm].
    """

    name: Optional[str] = None
    aquisition_date: Optional[datetime] = None
    experimenter: Optional[Experimenter] = None
    description: Optional[str] = None
    stage_label: Optional[StageLabel] = None

    # # UNUSED
    # experiment
    # experimenter_group
    # intrument
    # objective_settings
    # imaging_environment
    # stage_label
    # pixels
    # roi
    # microbeam_manipulation
    # annotation
