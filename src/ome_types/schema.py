import pickle
import re
from os.path import dirname, exists, join
from typing import Any, Dict, Optional

import xmlschema
from xmlschema.converters import XMLSchemaConverter

__cache__: Dict[str, xmlschema.XMLSchema] = {}


def camel_to_snake(name: str) -> str:
    # https://stackoverflow.com/a/1176023
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower().replace(" ", "_")


def get_schema(xml: str) -> xmlschema.XMLSchema:
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
            schema = xmlschema.XMLSchema(url)

            # FIXME Hack to work around xmlschema poor support for keyrefs to
            # substitution groups
            ns = "{http://www.openmicroscopy.org/Schemas/OME/2016-06}"
            ls_sgs = schema.maps.substitution_groups[f"{ns}LightSourceGroup"]
            ls_id_maps = schema.maps.identities[f"{ns}LightSourceIDKey"]
            ls_id_maps.elements = {e: None for e in ls_sgs}

            __cache__[version] = schema
            with open(local, "wb") as f:
                pickle.dump(__cache__[version], f)
    return __cache__[version]


def validate(xml: str, schema: Optional[xmlschema.XMLSchema] = None) -> None:
    schema = schema or get_schema(xml)
    schema.validate(xml)


class MyConverter(XMLSchemaConverter):
    def __init__(self, namespaces: Optional[Dict[str, Any]] = None):
        super().__init__(namespaces, attr_prefix="")

    def map_qname(self, qname: str) -> str:
        name = super().map_qname(qname)
        return camel_to_snake(name)

    def element_decode(self, data, xsd_element, xsd_type=None, level=0):  # type: ignore
        """Converts a decoded element data to a data structure."""
        result = super().element_decode(data, xsd_element, xsd_type, level)
        if isinstance(result, dict) and "$" in result:
            result["value"] = result.pop("$")
        # FIXME: Work out a better way to deal with concrete extensions of
        # abstract types.
        if xsd_element.local_name == "MetadataOnly":
            result = True
        elif xsd_element.local_name == "BinData":
            if result["length"] == 0 and "value" not in result:
                result["value"] = ""
        elif xsd_element.local_name == "Instrument":
            light_sources = []
            for _type in (
                "laser",
                "arc",
                "filament",
                "light_emitting_diode",
                "generic_excitation_source",
            ):
                if _type in result:
                    values = result.pop(_type)
                    if isinstance(values, dict):
                        values = [values]
                    for v in values:
                        v["_type"] = _type
                    light_sources.extend(values)
            if light_sources:
                result["light_source_group"] = light_sources
        elif xsd_element.local_name == "Union":
            shapes = []
            for _type in (
                "point",
                "line",
                "rectangle",
                "ellipse",
                "polyline",
                "polygon",
                "mask",
                "label",
            ):
                if _type in result:
                    values = result.pop(_type)
                    if isinstance(values, dict):
                        values = [values]
                    for v in values:
                        v["_type"] = _type
                    shapes.extend(values)
            result = shapes
        return result


def to_dict(  # type: ignore
    xml: str,
    schema: Optional[xmlschema.XMLSchema] = None,
    converter: XMLSchemaConverter = MyConverter,
    **kwargs,
) -> Dict[str, Any]:
    schema = schema or get_schema(xml)
    return schema.to_dict(xml, converter=converter, **kwargs)
