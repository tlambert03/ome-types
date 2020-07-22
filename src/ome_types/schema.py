import os
import re
from functools import lru_cache
from typing import Any, Dict, Optional, Union

import xmlschema
from xmlschema.converters import XMLSchemaConverter


def camel_to_snake(name: str) -> str:
    # https://stackoverflow.com/a/1176023
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower().replace(" ", "_")


@lru_cache(maxsize=8)
def _build_schema(url: str) -> xmlschema.XMLSchema:
    """Return Schema object for a url.

    For the special case of retrieving the 2016-06 OME Schema, use local file.
    """
    if url == "http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd":
        url = os.path.join(os.path.dirname(__file__), "ome-2016-06.xsd")

    schema = xmlschema.XMLSchema(url)
    # FIXME Hack to work around xmlschema poor support for keyrefs to
    # substitution groups
    ns = "{http://www.openmicroscopy.org/Schemas/OME/2016-06}"
    ls_sgs = schema.maps.substitution_groups[f"{ns}LightSourceGroup"]
    ls_id_maps = schema.maps.identities[f"{ns}LightSourceIDKey"]
    ls_id_maps.elements = {e: None for e in ls_sgs}
    return schema


def get_schema(source: Union[xmlschema.XMLResource, str]) -> xmlschema.XMLSchema:
    """Fetch an XMLSchema object given XML source.

    Parameters
    ----------
    source : XMLResource or str
        can be an :class:`xmlschema.XMLResource` instance, a file-like object, a path
        to a file or an URI of a resource or an Element instance or an ElementTree
        instance or a string containing the XML data.

    Returns
    -------
    xmlschema.XMLSchema
        An XMLSchema object for the source
    """
    return _build_schema(xmlschema.fetch_schema(source))


def validate(xml: str, schema: Optional[xmlschema.XMLSchema] = None) -> None:
    schema = schema or get_schema(xml)
    schema.validate(xml)


class OMEConverter(XMLSchemaConverter):
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
    converter: XMLSchemaConverter = OMEConverter,
    **kwargs,
) -> Dict[str, Any]:
    schema = schema or get_schema(xml)
    return schema.to_dict(xml, converter=converter, **kwargs)
