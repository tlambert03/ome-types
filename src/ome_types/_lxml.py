from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Container, MutableSequence, Union, cast

from typing_extensions import get_args

from . import model
from ._constants import OME_2016_06_XSD, URI_OME
from .model.shape_group import ShapeGroupType
from .util import _ensure_xml_bytes, _get_plural, camel_to_snake, cast_number, norm_key

NEED_INT = [s.__name__ for s in get_args(ShapeGroupType)]
NEED_INT.extend(["Channel", "Well"])


def _is_xml_comment(element: Element) -> bool:
    return False


if TYPE_CHECKING:
    import xml.etree.ElementTree

    import lxml.etree

    Element = Union[xml.etree.ElementTree.Element, lxml.etree._Element]
    ElementTree = Union[xml.etree.ElementTree.ElementTree, lxml.etree._ElementTree]
    Value = Union[float, str, int, bytearray, bool, dict[str, Any], list[Any]]
    Parser = Callable[[bytes], Element]

    XML: Parser
    tostring: Callable[[Element], bytes]
    parse: Callable[[str], ElementTree]

else:
    try:
        # faster if it's available
        from lxml.etree import XML, _Comment, parse, tostring

        def _is_xml_comment(element: Element) -> bool:
            return isinstance(element, _Comment)

    except ImportError:
        from xml.etree.ElementTree import XML, parse, tostring


def elem2dict(node: Element, exclude_null: bool = True) -> dict[str, Any]:
    """Convert an xml.etree or lxml.etree Element into a dict.

    Parameters
    ----------
    node : Element
        The Element to convert. Should be an `xml.etree.ElementTree.Element` or a
        `lxml.etree._Element`
    exclude_null : bool, optional
        If True, exclude keys with null values from the output.


    Returns
    -------
    dict[str, Any]
        The converted Element.
    """
    result: dict[str, Any] = {}

    # Re-used valued
    norm_node = norm_key(node.tag)
    # set of keys that are lists
    norm_list: Container = model._lists.get(norm_node, {})

    # Process attributes
    for key, val in node.attrib.items():
        is_list = key in norm_list
        key = camel_to_snake(norm_key(key))
        if norm_node in NEED_INT:
            val = cast_number(val)
        if is_list:
            key = _get_plural(key, node.tag)
            if key not in result:
                result[key] = []
            cast("list", result[key]).extend(val.split())
        else:
            result[key] = val

    # Process children
    for element in node:
        element = cast("Element", element)
        if _is_xml_comment(element):
            continue
        key = norm_key(element.tag)

        # Process element as tree element if inner XML contains non-whitespace content
        if element.text and element.text.strip():
            value: Any = element.text
            if element.attrib.items():
                value = {"value": value}
                for k, val in element.attrib.items():
                    value[camel_to_snake(norm_key(k))] = val

        elif key == "MetadataOnly":
            value = True

        else:
            value = elem2dict(element, exclude_null=exclude_null)
            if key == "XMLAnnotation":
                value["value"] = tostring(element[0])

        is_list = key in norm_list
        key = camel_to_snake(key)
        if is_list:
            if key == "bin_data" and value["length"] == "0" and "value" not in value:
                value["value"] = ""
            key = _get_plural(key, node.tag)
            if key not in result:
                result[key] = []
            cast("list", result[key]).append(value)

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
                result[key] = [value] if key.lower() == "m" else value
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


def validate_lxml(node: Element) -> Element:
    """Ensure that `node` is valid OMX XML.

    Raises
    ------
    lxml.etree.XMLSchemaValidateError
        If `node` is not valid OME XML.
    """
    # TODO: unify with xmlschema validate
    try:
        import lxml.etree
    except ImportError as e:
        raise ImportError("validating xml requires lxml") from e

    for key, val in node.attrib.items():
        if "schemaLocation" in key:
            ns, uri = val.split()
            if ns == URI_OME:
                uri = OME_2016_06_XSD
            schema_doc = parse(uri)  # noqa: S314
            break
    if not lxml.etree.XMLSchema(schema_doc).validate(node):
        raise lxml.etree.XMLSchemaValidateError(
            f"XML did not pass validation error against {uri}"
        )
    return node


def xml2dict(
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
    """
    root = XML(_ensure_xml_bytes(path_or_str))
    if validate:
        validate_lxml(root)

    return elem2dict(root)


def __getattr__(name: str) -> Any:
    """Import lxml if it is not already imported."""
    if name == "lxml2dict":
        import warnings

        warnings.warn(
            "lxml2dict is deprecated, use xml2dict instead",
            FutureWarning,
            stacklevel=2,
        )
        return xml2dict
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
