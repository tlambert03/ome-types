__version__ = "0.1.0"

from .autogen import convert_schema
from .schema import to_dict, validate

__all__ = ["convert_schema", "to_dict", "validate"]


# def from_xml(xml):
#     return OME(**to_dict(xml))
