from ome_types._mixins._base_type import OMEType
from xsdata_pydantic_basemodel.pydantic_compat import Field

__NAMESPACE__ = "http://www.openmicroscopy.org/Schemas/OME/2016-06"


class AffineTransform(OMEType):
    """A matrix used to transform the shape.

    ⎡ A00, A01, A02 ⎤ ⎢ A10, A11, A12 ⎥ ⎣ 0,   0,   1   ⎦
    """

    a00: float = Field(
        metadata={
            "name": "A00",
            "type": "Attribute",
            "required": True,
        }
    )
    a10: float = Field(
        metadata={
            "name": "A10",
            "type": "Attribute",
            "required": True,
        }
    )
    a01: float = Field(
        metadata={
            "name": "A01",
            "type": "Attribute",
            "required": True,
        }
    )
    a11: float = Field(
        metadata={
            "name": "A11",
            "type": "Attribute",
            "required": True,
        }
    )
    a02: float = Field(
        metadata={
            "name": "A02",
            "type": "Attribute",
            "required": True,
        }
    )
    a12: float = Field(
        metadata={
            "name": "A12",
            "type": "Attribute",
            "required": True,
        }
    )
