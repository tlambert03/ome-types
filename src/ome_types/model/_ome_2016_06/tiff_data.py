from typing import Optional, cast

from ome_types._base_type import OMEType

from .simple_types import NonNegativeInt, UniversallyUniqueIdentifier


class UUID(OMEType):
    file_name: str
    value: UniversallyUniqueIdentifier


class TiffData(OMEType):
    """This described the location of the pixel data in a tiff file.

    Parameters
    ----------
    first_c : NonNegativeInt, optional
        Gives the C position of the image plane at the specified IFD. Indexed
        from 0. Default is 0 (the first C position).
    first_t : NonNegativeInt, optional
        Gives the T position of the image plane at the specified IFD. Indexed
        from 0. Default is 0 (the first T position).
    first_z : NonNegativeInt, optional
        Gives the Z position of the image plane at the specified IFD. Indexed
        from 0. Default is 0 (the first Z position).
    ifd : NonNegativeInt, optional
        Gives the IFD(s) for which this element is applicable. Indexed from 0.
        Default is 0 (the first IFD).
    plane_count : NonNegativeInt, optional
        Gives the number of IFDs affected. Dimension order of IFDs is given by
        the enclosing Pixels element's DimensionOrder attribute. Default is
        the number of IFDs in the TIFF file, unless an IFD is specified, in
        which case the default is 1.
    uuid : Optional[UUID], optional
        This must be used when the IFDs are located in another file. Note: It
        is permissible for this to be self referential.
    """

    first_c: Optional[NonNegativeInt] = cast(NonNegativeInt, 0)
    first_t: Optional[NonNegativeInt] = cast(NonNegativeInt, 0)
    first_z: Optional[NonNegativeInt] = cast(NonNegativeInt, 0)
    ifd: Optional[NonNegativeInt] = cast(NonNegativeInt, 0)
    plane_count: Optional[NonNegativeInt] = None
    uuid: Optional[UUID] = None
