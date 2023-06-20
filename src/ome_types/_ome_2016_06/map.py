from typing import List

from pydantic import Field

from ome_types._base_type import OMEType


class M(OMEType):
    """This is a key/value pair used to build up a Mapping.

    The          Element and Attribute name are kept to single letters to minimize
    the          length at the expense of readability as they are likely to occur
    many          times.

    Parameters
    ----------
    k : str, optional
    """

    value: str
    k: str


class Map(OMEType):
    """This is a Mapping of key/value pairs.

    Parameters
    ----------
    k : str, optional
    m : M, optional
        This is a key/value pair used to build up a Mapping. The
        Element and Attribute name are kept to single letters to minimize the
        length at the expense of readability as they are likely to occur many
        times.
    """

    m: List[M] = Field(default_factory=list)
