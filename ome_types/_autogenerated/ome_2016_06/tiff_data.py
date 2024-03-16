from typing import Optional

from ome_types._mixins._base_type import OMEType
from xsdata_pydantic_basemodel.pydantic_compat import Field

__NAMESPACE__ = "http://www.openmicroscopy.org/Schemas/OME/2016-06"


class TiffData(OMEType):
    """
    This described the location of the pixel data in a tiff file.

    Attributes
    ----------
    uuid : None | "TiffData.UUID"
        This must be used when the IFDs are located in another file. Note: It is
        permissible for this to be self referential.
    ifd : int
        Gives the IFD(s) for which this element is applicable. Indexed from 0.
        Default is 0 (the first IFD). [units:none]
    first_z : int
        Gives the Z position of the image plane at the specified IFD. Indexed from
        0. Default is 0 (the first Z position). [units:none]
    first_t : int
        Gives the T position of the image plane at the specified IFD. Indexed from
        0. Default is 0 (the first T position). [units:none]
    first_c : int
        Gives the C position of the image plane at the specified IFD. Indexed from
        0. Default is 0 (the first C position). [units:none]
    plane_count : None | int
        Gives the number of IFDs affected. Dimension order of IFDs is given by the
        enclosing Pixels element's DimensionOrder attribute. Default is the number
        of IFDs in the TIFF file, unless an IFD is specified, in which case the
        default is 1. [units:none]
    """

    class Meta:
        namespace = "http://www.openmicroscopy.org/Schemas/OME/2016-06"

    uuid: Optional["TiffData.UUID"] = Field(
        default=None,
        metadata={
            "name": "UUID",
            "type": "Element",
        },
    )
    ifd: int = Field(
        default=0,
        metadata={
            "name": "IFD",
            "type": "Attribute",
            "min_inclusive": 0,
        },
        ge=0,
    )
    first_z: int = Field(
        default=0,
        metadata={
            "name": "FirstZ",
            "type": "Attribute",
            "min_inclusive": 0,
        },
        ge=0,
    )
    first_t: int = Field(
        default=0,
        metadata={
            "name": "FirstT",
            "type": "Attribute",
            "min_inclusive": 0,
        },
        ge=0,
    )
    first_c: int = Field(
        default=0,
        metadata={
            "name": "FirstC",
            "type": "Attribute",
            "min_inclusive": 0,
        },
        ge=0,
    )
    plane_count: Optional[int] = Field(
        default=None,
        metadata={
            "name": "PlaneCount",
            "type": "Attribute",
            "min_inclusive": 0,
        },
        ge=0,
    )

    class UUID(OMEType):
        """
        Attributes
        ----------
        value : str
            (The UUID value).
        file_name : None | str
            This can be used when the IFDs are located in another file. The / (forward
            slash) is used as the path separator. A relative path is recommended.
            However an absolute path can be specified. Default is to use the file the
            ome-xml data has been pulled from. Note: It is permissible for this to be
            self referential. The file image1.tiff may contain ome-xml data that has
            FilePath="image1.tiff" or "./image1.tiff"
        """

        value: str = Field(
            default="",
            metadata={
                "required": True,
                "pattern": r"(urn:uuid:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})",
            },
            regex="(urn:uuid:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})",
        )
        file_name: Optional[str] = Field(
            default=None,
            metadata={
                "name": "FileName",
                "type": "Attribute",
            },
        )


UUID = TiffData.UUID
