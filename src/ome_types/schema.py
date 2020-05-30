import pickle
import re
from os.path import dirname, exists, join
from typing import Dict

import xmlschema

__cache__: Dict[str, xmlschema.XMLSchema] = {}


def camel_to_snake(name):
    # https://stackoverflow.com/a/1176023
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower().replace(" ", "_")


def get_schema(xml):
    url = xmlschema.fetch_schema(xml)
    version = (
        re.split("(.com|.org)", url)[-1]
        .replace("/", "_")
        .lstrip("_")
        .replace(".xsd", "")
    )
    if version not in __cache__:
        local = join(dirname(__file__), f"{version}.pkl")
        if exists(local):
            with open(local, "rb") as f:
                __cache__[version] = pickle.load(f)
        else:
            __cache__[version] = xmlschema.XMLSchema(url)
            with open(local, "wb") as f:
                pickle.dump(__cache__[version], f)
    return __cache__[version]


def validate(xml: str, schema=None):
    schema = schema or get_schema(xml)
    schema.validate(xml)


class MyConverter(xmlschema.converters.XMLSchemaConverter):
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


def to_dict(xml: str, schema=None, converter=MyConverter, **kwargs):
    schema = schema or get_schema(xml)
    return schema.to_dict(xml, converter=converter, **kwargs)
