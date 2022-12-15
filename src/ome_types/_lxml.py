from __future__ import annotations

from pathlib import Path
from typing import Any, MutableSequence

import lxml.etree
from typing_extensions import get_args

from . import model
from ._constants import OME_2016_06_XSD, URI_OME
from .model.shape_group import ShapeGroupType
from .util import _ensure_xml_bytes, _get_plural, camel_to_snake, cast_number, norm_key

NEED_INT = [s.__name__ for s in get_args(ShapeGroupType)]
NEED_INT.extend(["Channel", "Well"])


def elem2dict(
    node: lxml.etree._Element, parent_name: str | None = None, exclude_null: bool = True
) -> dict[str, Any]:
    """Convert an lxml.etree node tree into a dict."""
    result: dict[str, Any] = {}

    # Re-used valued
    norm_node = norm_key(node.tag)
    norm_list: set[str] | dict[Any, Any] = model._lists.get(norm_node, {})

    for key, val in node.attrib.items():
        is_list = key in norm_list
        key = camel_to_snake(norm_key(key))
        if norm_node in NEED_INT:
            val = cast_number(val)
        if is_list:
            key = _get_plural(key, node.tag)
            if key not in result:
                result[key] = []
            result[key].extend(val.split())
        else:
            result[key] = val

    for element in node.iterchildren():
        if isinstance(element, lxml.etree._Comment):
            continue
        key = norm_key(element.tag)

        # Process element as tree element if inner XML contains non-whitespace content
        if element.text and element.text.strip():

            value = element.text
            if element.attrib.items():
                value = {"value": value}
                for k, val in element.attrib.items():
                    value[camel_to_snake(norm_key(k))] = val

        elif key == "MetadataOnly":
            value = True

        else:
            value = elem2dict(element, norm_node)
            if key == "XMLAnnotation":
                value["value"] = lxml.etree.tostring(element[0])

        is_list = key in norm_list
        key = camel_to_snake(key)
        if is_list:
            if key == "bin_data":
                if value["length"] == "0" and "value" not in value:
                    value["value"] = ""
            key = _get_plural(key, node.tag)
            if key not in result:
                result[key] = []
            result[key].append(value)

        elif key == "structured_annotations":
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
                if _type in value:
                    values = value.pop(_type)
                    if not isinstance(values, list):
                        values = [values]

                    for v in values:
                        v["_type"] = _type

                        # Normalize empty element to zero-length string.
                        if "value" not in v or v["value"] is None:
                            v["value"] = ""
                    annotations.extend(values)

            if key in result:
                raise ValueError("Duplicate structured_annotations")
            result[key] = annotations

        elif value or not exclude_null:
            try:
                rv = result[key]
            except KeyError:
                if key == "m":
                    result[key] = [value]
                else:
                    result[key] = value
            else:
                if not isinstance(rv, MutableSequence) or not rv:
                    result[key] = [rv, value]
                elif isinstance(rv[0], MutableSequence) or not isinstance(
                    value, MutableSequence
                ):
                    rv.append(value)
                else:
                    result[key] = [result, value]

    return result


def validate_lxml(node: lxml.etree._Element) -> lxml.etree._Element:
    """Ensure that `node` is valid OMX XML.

    Raises
    ------
    lxml.etree.XMLSchemaValidateError
        If `node` is not valid OME XML.
    """
    for key, val in node.attrib.items():
        if "schemaLocation" in key:
            ns, uri = val.split()
            if ns == URI_OME:
                schema_doc = lxml.etree.parse(OME_2016_06_XSD)
            else:
                schema_doc = lxml.etree.parse(uri)
            break
    if not lxml.etree.XMLSchema(schema_doc).validate(node):
        raise lxml.etree.XMLSchemaValidateError(
            f"XML did not pass validation error against {uri}"
        )
    return node


def lxml2dict(
    path_or_str: Path | str | bytes, validate: bool | None = False
) -> dict[str, Any]:
    """Convert XML string or path to dict using lxml.

    xml : Union[Path, str, bytes]
        XML string, bytes, or path to XML file.
    validate : Optional[bool]
        Whether to validate XML as valid OME XML, by default False.

    Returns
    -------
    Dict[str, Any]
        OME dict

    Raises
    ------
    TypeError
        _description_
    """
    result = lxml.etree.XML(_ensure_xml_bytes(path_or_str))
    if validate:
        validate_lxml(result)

    return elem2dict(result)
