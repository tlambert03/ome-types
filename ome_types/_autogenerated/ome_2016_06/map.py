from typing import ClassVar, List, Optional

from pydantic_compat import model_validator

from ome_types._mixins._base_type import OMEType
from ome_types._mixins._map_mixin import MapMixin
from ome_types._mixins._validators import validate_map_annotation
from xsdata_pydantic_basemodel.pydantic_compat import Field

__NAMESPACE__ = "http://www.openmicroscopy.org/Schemas/OME/2016-06"


class Map(OMEType, MapMixin):
    """
    This is a Mapping of key/value pairs.

    Attributes
    ----------
    ms : list["Map.M"]
        This is a key/value pair used to build up a Mapping. The Element and
        Attribute name are kept to single letters to minimize the length at the
        expense of readability as they are likely to occur many times.
    """

    ms: List["Map.M"] = Field(
        default_factory=list,
        metadata={
            "name": "M",
            "type": "Element",
            "namespace": "http://www.openmicroscopy.org/Schemas/OME/2016-06",
        },
    )

    class M(OMEType):
        value: str = Field(
            default="",
            metadata={
                "required": True,
            },
        )
        k: Optional[str] = Field(
            default=None,
            metadata={
                "name": "K",
                "type": "Attribute",
            },
        )

    _v_map = model_validator(mode="before")(validate_map_annotation)
    dict: ClassVar = MapMixin._pydict
    __iter__: ClassVar = MapMixin.__iter__


M = Map.M
