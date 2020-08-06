import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Union
from xml.etree import ElementTree

import xmlschema
from xmlschema.converters import XMLSchemaConverter

from .model import _field_plurals

URI_OME = "http://www.openmicroscopy.org/Schemas/OME/2016-06"
NS_OME = "{" + URI_OME + "}"

__cache__: Dict[str, xmlschema.XMLSchema] = {}


def camel_to_snake(name: str) -> str:
    # https://stackoverflow.com/a/1176023
    result = re.sub("([A-Z]+)([A-Z][a-z]+)", r"\1_\2", name)
    result = re.sub("([a-z0-9])([A-Z])", r"\1_\2", result)
    result = result.lower().replace(" ", "_")
    return result


@lru_cache(maxsize=8)
def _build_schema(namespace: str) -> xmlschema.XMLSchema:
    """Return Schema object for a url.

    For the special case of retrieving the 2016-06 OME Schema, use local file.
    """
    if namespace == URI_OME:
        schema = xmlschema.XMLSchema(str(Path(__file__).parent / "ome-2016-06.xsd"))
        # FIXME Hack to work around xmlschema poor support for keyrefs to
        # substitution groups
        ls_sgs = schema.maps.substitution_groups[f"{NS_OME}LightSourceGroup"]
        ls_id_maps = schema.maps.identities[f"{NS_OME}LightSourceIDKey"]
        ls_id_maps.elements = {e: None for e in ls_sgs}
    else:
        schema = xmlschema.XMLSchema(namespace)
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
    if not isinstance(source, xmlschema.XMLResource):
        resource = xmlschema.XMLResource(source)
    else:
        resource = source
    return _build_schema(resource.namespace)


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
        elif xsd_element.local_name == "StructuredAnnotations":
            annotations = []
            for _type in (
                "boolean_annotation",
                "comment_annotation",
                "double_annotation",
                "file_annotation",
                "list_annotation",
                "long_annotation",
                "tag_annotation",
                "term_annotation",
                "timestamp_annotation",
                "xml_annotation",
            ):
                if _type in result:
                    values = result.pop(_type)
                    for v in values:
                        v["_type"] = _type
                        # Normalize empty element to zero-length string.
                        if "value" in v and v["value"] is None:
                            v["value"] = ""
                    annotations.extend(values)
            result = annotations
        if isinstance(result, dict):
            for name in list(result.keys()):
                plural = _field_plurals.get((xsd_element.local_name, name), None)
                if plural:
                    value = result.pop(name)
                    assert isinstance(value, list), "expected list for plural attr"
                    result[plural] = value
        return result


def to_dict(  # type: ignore
    xml: str,
    schema: Optional[xmlschema.XMLSchema] = None,
    converter: XMLSchemaConverter = OMEConverter,
    **kwargs,
) -> Dict[str, Any]:
    schema = schema or get_schema(xml)
    result = schema.to_dict(xml, converter=converter, **kwargs)
    # xmlschema doesn't provide usable access to mixed XML content, so we'll
    # fill the XMLAnnotation value attributes ourselves by re-parsing the XML
    # with ElementTree and using the Element objects as the values.
    tree = None
    for annotation in result.get("structured_annotations", []):
        if annotation["_type"] == "xml_annotation":
            if tree is None:
                tree = ElementTree.parse(xml)
            aid = annotation["id"]
            elt = tree.find(f".//{NS_OME}XMLAnnotation[@ID='{aid}']/{NS_OME}Value")
            annotation["value"] = elt
    return result
