from __future__ import annotations

import os.path
from collections import defaultdict
from datetime import datetime
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import IO, Any, Union
from xml.etree import ElementTree

import xmlschema
from xmlschema import ElementData, XMLSchemaParseError
from xmlschema.converters import XMLSchemaConverter
from xmlschema.exceptions import XMLSchemaValueError

from ome_types._base_type import OMEType

from . import util
from ._constants import NS_OME, NS_XSI, OME_2016_06_XSD, SCHEMA_LOC_OME, URI_OME
from .model import (
    OME,
    XMLAnnotation,
    _camel_to_snake,
    _plural_to_singular,
    _singular_to_plural,
    _snake_to_camel,
    simple_types,
)

__cache__: dict[str, xmlschema.XMLSchema] = {}
_XMLSCHEMA_VERSION: tuple[int, ...] = tuple(
    int(v) if v.isnumeric() else v for v in xmlschema.__version__.split(".")
)

XMLSourceType = Union[str, bytes, Path, IO[str], IO[bytes]]


@lru_cache(maxsize=8)
def _build_schema(ns: str, uri: str | None = None) -> xmlschema.XMLSchema:
    """Return Schema object for a url.

    For the special case of retrieving the 2016-06 OME Schema, use local file.
    """
    if ns == URI_OME:
        schema = xmlschema.XMLSchema(OME_2016_06_XSD)
        # FIXME Hack to work around xmlschema poor support for keyrefs to
        # substitution groups
        ls_sgs = schema.maps.substitution_groups[f"{NS_OME}LightSourceGroup"]
        ls_id_maps = schema.maps.identities[f"{NS_OME}LightSourceIDKey"]
        ls_id_maps.elements = {e: None for e in ls_sgs}
    else:
        schema = xmlschema.XMLSchema(uri)
    return schema


def get_schema(source: xmlschema.XMLResource | XMLSourceType) -> xmlschema.XMLSchema:
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
        source = xmlschema.XMLResource(source)

    for ns, uri in source.get_locations():
        try:
            return _build_schema(ns, uri)
        except XMLSchemaParseError:
            pass
    raise XMLSchemaValueError(f"Could not find a schema for XML resource {source!r}.")


def validate(xml: XMLSourceType, schema: xmlschema.XMLSchema | None = None) -> None:
    schema = schema or get_schema(xml)
    schema.validate(xml)


class OMEConverter(XMLSchemaConverter):
    def __init__(
        self, namespaces: dict[str, Any] | None = None, **kwargs: dict[Any, Any]
    ):
        self._ome_ns = ""
        super().__init__(namespaces, attr_prefix="")
        for name, uri in self._namespaces.items():
            if uri == URI_OME:
                self._ome_ns = name

    def map_qname(self, qname: str) -> str:
        name = super().map_qname(qname)
        if name.lower().startswith(self._ome_ns):
            name = name[len(self._ome_ns) :].lstrip(":")
        return _camel_to_snake.get(name, name)

    def element_decode(self, data, xsd_element, xsd_type=None, level=0):  # type: ignore
        """Convert a decoded element data to a data structure."""
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
        elif xsd_element.local_name == "StructuredAnnotations":
            annotations = []
            for _type in (
                "boolean_annotation",
                "comment_annotation",
                "double_annotation",
                "file_annotation",
                "list_annotation",
                "long_annotation",
                "map_annotation",
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
                plural = _singular_to_plural.get((xsd_element.local_name, name), None)
                if plural:
                    value = result.pop(name)
                    if not isinstance(value, list):
                        raise TypeError("expected list for plural attr")
                    result[plural] = value
        return result

    def element_encode(
        self, obj: Any, xsd_element: xmlschema.XsdElement, level: int = 0
    ) -> ElementData:
        tag = xsd_element.qualified_name
        if not isinstance(obj, OMEType):
            if isinstance(obj, datetime):
                return ElementData(
                    tag, obj.isoformat().replace("+00:00", "Z"), None, {}
                )
            elif isinstance(obj, ElementTree.Element):
                # ElementData can't represent mixed content, so we'll leave this
                # element empty and fix it up after encoding is complete.
                return ElementData(tag, None, None, {})
            elif xsd_element.type.simple_type is not None:
                return ElementData(tag, obj, None, {})
            elif xsd_element.local_name == "MetadataOnly":
                return ElementData(tag, None, None, {})
            elif xsd_element.local_name in {"Union", "StructuredAnnotations"}:
                names = [type(v).__name__ for v in obj]
                content = [(f"{NS_OME}{n}", v) for n, v in zip(names, obj)]
                return ElementData(tag, None, content, {})
            else:
                raise NotImplementedError(
                    "Encountered a combination of schema element and data type"
                    " that is not yet supported. Please submit a bug report with"
                    " the information below:"
                    f"\n    element: {xsd_element}\n    data type: {type(obj)}"
                )
        text = None
        content = []
        attributes = {}
        # FIXME Can we simplify this?
        tag_index = defaultdict(
            lambda: -1,
            ((_camel_to_snake[e.local_name], i) for i, e in enumerate(xsd_element)),
        )
        _fields = obj.__fields__.values()
        for field in sorted(
            _fields,
            key=lambda f: tag_index[_plural_to_singular.get(f.name, f.name)],
        ):
            name = field.name
            if name.endswith("_"):
                continue
            default = (
                field.default_factory() if field.default_factory else field.default
            )
            value = getattr(obj, name)
            if value == default or name == "metadata_only" and not value:
                continue
            if isinstance(value, simple_types.Color):
                value = value.as_int32()
            name = _plural_to_singular.get(name, name)
            name = _snake_to_camel.get(name, name)
            if name in xsd_element.attributes:
                if isinstance(value, list):
                    value = [getattr(i, "value", i) for i in value]
                elif isinstance(value, Enum):
                    value = value.value
                elif isinstance(value, datetime):
                    value = value.isoformat().replace("+00:00", "Z")
                attributes[name] = value
            elif name == "Value" and xsd_element.local_name in {"BinData", "UUID", "M"}:
                text = value
            else:
                if not isinstance(value, list) or name in {
                    "Union",
                    "StructuredAnnotations",
                }:
                    value = [value]
                if name == "LightSourceGroup":
                    names = [type(v).__name__ for v in value]
                else:
                    names = [name] * len(value)
                content.extend([(f"{NS_OME}{n}", v) for n, v in zip(names, value)])
        return ElementData(tag, text, content, attributes)


def xmlschema2dict(
    xml: str,
    schema: xmlschema.XMLSchema | None = None,
    converter: XMLSchemaConverter = OMEConverter,
    validate: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    if isinstance(xml, bytes):
        xml = xml.decode("utf-8")

    schema = schema or get_schema(xml)

    if _XMLSCHEMA_VERSION >= (2,):
        kwargs["validation"] = "strict" if validate else "lax"

    result = xmlschema.to_dict(xml, schema=schema, converter=converter, **kwargs)

    if _XMLSCHEMA_VERSION >= (2,) and not validate:
        result, _ = result
    # xmlschema doesn't provide usable access to mixed XML content, so we'll
    # fill the XMLAnnotation value attributes ourselves by re-parsing the XML
    # with ElementTree and using the Element objects as the values.
    tree = None
    for annotation in result.get("structured_annotations", []):
        if annotation["_type"] == "xml_annotation":
            if tree is None:
                from io import StringIO

                # determine if we're dealing with a raw XML string or a filepath
                # very long XML strings will raise ValueError on Windows.
                try:
                    _xml = xml if os.path.exists(xml) else StringIO(xml)
                except ValueError:
                    _xml = StringIO(xml)

                tree = ElementTree.parse(_xml)  # type: ignore  # noqa: S314
            aid = annotation["id"]
            elt = tree.find(f".//{NS_OME}XMLAnnotation[@ID='{aid}']/{NS_OME}Value")
            annotation["value"] = elt
    return result


def to_xml_element(ome: OME) -> ElementTree.Element:
    schema = _build_schema(URI_OME)
    root = schema.encode(
        ome, path=f"/{NS_OME}OME", converter=OMEConverter, use_defaults=False
    )
    # Patch up the XML element tree with Element objects from XMLAnnotations to
    # work around xmlschema's lack of support for mixed content.
    for oid, obj in util.collect_ids(ome).items():
        if isinstance(obj, XMLAnnotation):
            elt = root.find(f".//{NS_OME}XMLAnnotation[@ID='{oid}']/{NS_OME}Value")
            elt.extend(list(obj.value))
    root.attrib[f"{NS_XSI}schemaLocation"] = SCHEMA_LOC_OME
    return root


def to_xml(ome: OME, **kwargs: Any) -> str:
    """
    Dump an OME object to string.

    Parameters
    ----------
    ome: OME
        OME object to dump.
    **kwargs
        Extra kwargs to pass to ElementTree.tostring.

    Returns
    -------
    ome_string: str
        The XML string of the OME object.
    """
    root = to_xml_element(ome)
    ElementTree.register_namespace("", URI_OME)
    kwargs.setdefault("encoding", "unicode")
    kwargs.setdefault("method", "xml")
    return ElementTree.tostring(root, **kwargs)
