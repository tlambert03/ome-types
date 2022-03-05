from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from ._base_type import OMEType
from .model.reference import Reference
from .model.simple_types import LSID

URI_OME = "http://www.openmicroscopy.org/Schemas/OME/2016-06"
NS_OME = "{" + URI_OME + "}"

if TYPE_CHECKING:
    import lxml.etree

try:
    from lxml import etree
except ModuleNotFoundError:
    # Maybe when a logger is created, issue a warning
    pass


def collect_references(value: Any) -> List[Reference]:
    """Return a list of all References contained in value.

    Recursively walks all dataclass fields and iterates over lists. The base
    case is when value is either a Reference object, or an uninteresting type
    that we don't need to inspect further.

    """
    references: List[Reference] = []
    if isinstance(value, Reference):
        references.append(value)
    elif isinstance(value, list):
        for v in value:
            references.extend(collect_references(v))
    elif isinstance(value, OMEType):
        for f in value.__fields__:
            references.extend(collect_references(getattr(value, f)))
    # Do nothing for uninteresting types
    return references


def collect_ids(value: Any) -> Dict[LSID, OMEType]:
    """Return a map of all model objects contained in value, keyed by id.

    Recursively walks all dataclass fields and iterates over lists. The base
    case is when value is neither a dataclass nor a list.

    """
    ids: Dict[LSID, OMEType] = {}
    if isinstance(value, list):
        for v in value:
            ids.update(collect_ids(v))
    elif isinstance(value, OMEType):
        for f in value.__fields__:
            if f == "id" and not isinstance(value, Reference):
                # We don't need to recurse on the id string, so just record it
                # and move on.
                ids[value.id] = value  # type: ignore
            else:
                ids.update(collect_ids(getattr(value, f)))
    # Do nothing for uninteresting types.
    return ids


def camel_to_snake(name: str) -> str:
    import re

    result = re.sub("([A-Z]+)([A-Z][a-z]+)", r"\1_\2", name)
    result = re.sub("([a-z0-9])([A-Z])", r"\1_\2", result)
    return result.lower().replace(" ", "_")


def norm_key(key: str):

    return etree.QName(key).localname


def elem2dict(node: "lxml.etree._Element", exclude_null=True) -> Dict[str, Any]:
    """
    Convert an lxml.etree node tree into a dict.
    """
    from .model import _lists, _singular_to_plural

    result: Dict[str, Any] = {}

    for key, val in node.attrib.items():
        is_list = key in _lists.get(norm_key(node.tag), {})
        key = camel_to_snake(norm_key(key))
        if is_list:
            key = _get_plural(key, node.tag)
            if key not in result:
                result[key] = []
            result[key].append(val)
        else:
            result[key] = val

    for element in node.iterchildren():
        if isinstance(element, etree._Comment):
            continue
        key = norm_key(element.tag)
        # Process element as tree element if the inner XML contains non-whitespace content
        if element.text and element.text.strip():
            value = element.text
            if element.attrib.items():
                value = {"value": value}
                for k, val in element.attrib.items():
                    value[camel_to_snake(norm_key(k))] = val

        else:
            value = elem2dict(element)

        is_list = key in _lists.get(norm_key(node.tag), {})
        key = camel_to_snake(key)
        if is_list:
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

                        # Special catch for xml_annotations
                        if _type == "xml_annotation":
                            aid = v["id"]
                            elt = element.find(
                                f".//{NS_OME}XMLAnnotation[@ID='{aid}']/{NS_OME}Value"
                            )
                            v["value"] = etree.tostring(elt)

                        # Normalize empty element to zero-length string.
                        if "value" in v and v["value"] is None:
                            v["value"] = ""
                    annotations.extend(values)

            assert key not in result.keys()
            result[key] = annotations
        elif value or not exclude_null:
            if key in result.keys():
                if not isinstance(result[key], list):
                    result[key] = [result[key]]
                result[key].append(value)
            else:
                result[key] = value

    return result


def _get_plural(key, tag):
    from .model import _singular_to_plural

    try:
        return _singular_to_plural[(etree.QName(tag).localname, key)]
    except KeyError:
        return f"{key}s"


def lxml2dict(path_or_str) -> dict:
    if hasattr(path_or_str, "read"):
        text = path_or_str.read().encode()
    else:
        text = Path(path_or_str).read_bytes()

    return elem2dict(etree.XML(text))
