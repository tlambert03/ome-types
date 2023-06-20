from ome_types._base_type import OMEType

from .reference import Reference


class Settings(Reference, OMEType):
    """Settings is an empty complex type that is contained and extended by all the
    `*Settings` elements Each `*Settings` element defines an attribute named ID of
    simple type `*ID` and the other information that is needed.

    Each simple type `*ID` is restricted to the base type LSID with an appropriate
    pattern
    """
