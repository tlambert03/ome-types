__version__ = "0.1.0"

from .autogen import convert_schema, camel_to_snake
from .schema import to_dict, validate

__all__ = ["convert_schema", "to_dict", "validate"]


from xmlschema.converters import XMLSchemaConverter

try:
    from .model import OME
except ImportError:
    OME = None


class MyConv(XMLSchemaConverter):
    def __init__(self, namespaces=None):
        super().__init__(namespaces, attr_prefix="")

    def map_qname(self, qname):
        name = super().map_qname(qname)
        return camel_to_snake(name)

    def element_decode(self, data, xsd_element, xsd_type=None, level=0) -> dict:
        """Converts a decoded element data to a data structure."""
        result = super().element_decode(data, xsd_element, xsd_type, level)
        if result and "$" in result:
            result["value"] = result.pop("$")
        return result


def from_xml(xml, OME=OME):

    d = to_dict(xml, converter=MyConv)
    for key in list(d.keys()):
        if key.startswith(("xml", "xsi")):
            d.pop(key)

    return OME(**d)
