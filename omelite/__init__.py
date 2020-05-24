__version__ = "0.1.0"

from .autogen import convert_schema
from .schema import to_dict, validate

__all__ = ["convert_schema", "to_dict", "validate", "from_xml"]


try:
    from .model import OME
except ImportError:
    print("model not found ... running autogeneration")
    convert_schema()
    from .model import OME


def from_xml(xml, OME=OME) -> OME:

    d = to_dict(xml)
    for key in list(d.keys()):
        if key.startswith(("xml", "xsi")):
            d.pop(key)

    return OME(**d)
