from __future__ import annotations

import importlib
import operator
import os
import warnings
from dataclasses import is_dataclass
from pathlib import Path
from struct import Struct
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from ome_types.validation import validate_xml

try:
    from lxml import etree as ET
except ImportError:  # pragma: no cover
    from xml.etree import ElementTree as ET  # type: ignore[no-redef]

from xsdata.formats.dataclass.parsers.config import ParserConfig

from xsdata_pydantic_basemodel.bindings import (
    SerializerConfig,
    XmlParser,
    XmlSerializer,
)

if TYPE_CHECKING:
    import io
    from typing import TypedDict

    from xsdata.formats.dataclass.parsers.mixins import XmlHandler

    from ome_types._mixins._base_type import OMEType
    from ome_types.model import OME
    from xsdata_pydantic_basemodel.bindings import XmlContext

    class ParserKwargs(TypedDict, total=False):
        config: ParserConfig
        context: XmlContext
        handler: type[XmlHandler]


__all__ = ["from_xml", "to_xml", "to_dict", "from_tiff", "tiff2xml"]

OME_ROOT = "http://www.openmicroscopy.org/Schemas/OME"
OME_2016_06_URI = f"{OME_ROOT}/2016-06"
MODULES = {
    OME_2016_06_URI: "ome_types._autogenerated.ome_2016_06",
}
TRANSFORMS_PATH = Path(__file__).parent / "transforms"
TRANSFORMS = {
    f"{OME_ROOT}/{p.name.split('-to')[0]}": p for p in TRANSFORMS_PATH.glob("*.xsl")
}


def apply_transform(root: ET.Element, transform: Path) -> ET._Element:
    from lxml import etree

    # Create a transformer object
    transformer = etree.XSLT(ET.parse(str(transform)))
    result = transformer(root).getroot()

    *_ns, _ = result.tag[1:].split("}", 1)
    ns = next(iter(_ns), None)
    if ns in TRANSFORMS:
        return apply_transform(result, TRANSFORMS[ns])
    if ns != OME_2016_06_URI:
        raise ValueError(
            f"Failed to update namespace {ns!r} to {OME_2016_06_URI!r} in {transform!r}"
        )
    return result


def _get_ome_type(xml: str | bytes) -> tuple[ET._Element, type[OMEType]]:
    """Resolve a python model class for the root element of an OME XML document."""
    if isinstance(xml, str) and not xml.lstrip().startswith("<"):
        root = ET.parse(xml).getroot()
    else:
        if not isinstance(xml, bytes):
            xml = xml.encode("utf-8")
        root = ET.fromstring(xml)

    *_ns, localname = root.tag[1:].split("}", 1)
    ns = next(iter(_ns), None)

    if ns in TRANSFORMS:
        root = apply_transform(root, TRANSFORMS[ns])
        *_, localname = root.tag[1:].split("}", 1)
    elif ns != OME_2016_06_URI:
        raise ValueError(f"Unsupported OME schema tag {root.tag!r} in namespace {ns!r}")

    mod = importlib.import_module(MODULES[OME_2016_06_URI])
    try:
        return root, getattr(mod, localname)
    except AttributeError as e:  # pragma: no cover
        raise ValueError(
            f"Could not find a class for {localname!r} in {mod.__name__}"
        ) from e


def to_dict(source: OME | Path | str | bytes) -> dict[str, Any]:
    """Return a dictionary representation of an OME or XML document.

    Parameters
    ----------
    source : OME | Path | str | bytes
        An OME object, or a path to an XML file, or a string or bytes containing XML.

    Returns
    -------
    dict[str, Any]
        A dictionary representation of the OME object or XML document.
    """
    if is_dataclass(source):  # pragma: no cover
        raise NotImplementedError("dataclass -> dict is not supported yet")

    if isinstance(source, BaseModel):
        return source.dict(exclude_defaults=True)

    return from_xml(  # type: ignore[return-value]
        source,
        # the class_factory is what prevents class instantiation,
        # simply returning the params instead
        parser_kwargs={"config": ParserConfig(class_factory=lambda a, b: b)},
    )


def from_xml(
    xml: Path | str | bytes,
    *,
    validate: bool | None = None,
    parser: Any = None,
    parser_kwargs: ParserKwargs | None = None,
) -> OME:  #  Not totally true, see note below
    """Generate an OME object from an XML document.

    NOTE: Technically, this can return any ome-types instance, (not just OME) but it's
    by far the most common type that will come out of this function, and the type
    annotation will be more useful to most users. For those who pass in an xml document
    that isn't just a root <OME> tag, they can cast the result to the correct type
    themselves.

    Parameters
    ----------
    xml : Path | str | bytes
        Path to an XML file, or a string or bytes containing XML.
    validate : bool | None
        Whether to validate the XML document against the OME schema.
        If None, validation will be skipped if lxml is not available,
        and will be performed otherwise.
    parser : Any
        Ignored, but kept for backwards compatibility.
    parser_kwargs : ParserKwargs | None
        Passed to the XmlParser constructor. If None, a default parser
        will be used.

    Returns
    -------
    OME
        The OME object parsed from the XML document. (See NOTE above.)
    """
    if parser is not None:  # pragma: no cover
        warnings.warn(
            "As of version 0.4.0, the parser argument is ignored. "
            "lxml will be used if available in the environment, but you can "
            "drop this keyword argument.",
            DeprecationWarning,
            stacklevel=2,
        )

    if isinstance(xml, Path):
        xml = str(xml)
    # this cast is a lie... see NOTE above.
    root, OME_type = _get_ome_type(xml)
    xml = str(ET.tostring(root, encoding="utf-8"), encoding="utf-8")

    if validate:
        validate_xml(xml)

    parser_ = XmlParser(**(parser_kwargs or {}))
    if isinstance(xml, bytes):
        return parser_.from_bytes(xml, OME_type)
    if os.path.isfile(xml):
        return parser_.parse(xml, OME_type)
    return parser_.from_string(xml, OME_type)


def to_xml(
    ome: OMEType,
    *,
    # exclude_defaults takes precedence over exclude_unset
    # if a value equals the default, it will be excluded
    exclude_defaults: bool = False,
    # exclude_unset will exclude any value that is not explicitly set
    # but will INCLUDE values that are set to their default
    exclude_unset: bool = True,
    indent: int = 2,
    include_namespace: bool | None = None,
    include_schema_location: bool = True,
    canonicalize: bool = False,
    validate: bool = False,
) -> str:
    """Generate an XML document from an OME object.

    Parameters
    ----------
    ome : OMEType
        Instance of an ome-types model class.
    exclude_defaults : bool, optional
        Whether to exclude attributes that are set to their default value,
        by default False.
    exclude_unset : bool, optional
        Whether to exclude attributes that are not explicitly set,
        by default True.
    indent : int, optional
        Number of spaces to indent the XML document, by default 2.
    include_namespace : bool | None, optional
        Whether to include the OME namespace in the root element.  If `None`, will
        be set to the value of `canonicalize`, by default None.
    include_schema_location : bool, optional
        Whether to include the schema location in the root element, by default True.
    canonicalize : bool, optional
        Whether to canonicalize the XML output, by default False.
    validate : bool, optional
        Whether to validate the XML document against the OME schema, after rendering.
        (In most cases, this will be redundant and unnecessary.)

    Returns
    -------
    str
        The XML document as a string.
    """
    config = SerializerConfig(
        pretty_print=(indent > 0) and not canonicalize,  # canonicalize does it for us
        pretty_print_indent=" " * indent,
        xml_declaration=False,
        ignore_default_attributes=exclude_defaults,
        ignore_unset_attributes=exclude_unset,
        attribute_sort_key=operator.attrgetter("name") if canonicalize else None,
    )
    if include_schema_location:
        config.schema_location = f"{OME_2016_06_URI} {OME_2016_06_URI}/ome.xsd"

    serializer = XmlSerializer(config=config)
    if include_namespace is None:
        include_namespace = canonicalize

    ns_map = {"ome" if include_namespace else None: OME_2016_06_URI}
    xml = serializer.render(ome, ns_map=ns_map)

    if canonicalize:
        xml = _canonicalize(xml, indent=" " * indent)
    if validate:
        validate_xml(xml)
    return xml


def _canonicalize(xml: str, indent: str) -> str:
    from xml.dom import minidom

    xml_out = ET.canonicalize(xml, strip_text=True)
    return minidom.parseString(xml_out).toprettyxml(indent=indent)  # noqa: S318


def from_tiff(
    path: Path | str,
    *,
    validate: bool | None = None,
    parser_kwargs: ParserKwargs | None = None,
) -> OME:
    """Generate an OME object from a TIFF file.

    Parameters
    ----------
    path : Path | str
        Path to a TIFF file.
    validate : bool | None
        Whether to validate the XML document against the OME schema before parsing.
        If None, validation will be skipped if lxml is not available,
        and will be performed otherwise.
    parser_kwargs : ParserKwargs | None
        Passed to the XmlParser constructor. If None, a default parser
        will be used.
    """
    xml = tiff2xml(path)
    return from_xml(xml, validate=validate, parser_kwargs=parser_kwargs)


TIFF_TYPES: dict[bytes, tuple[Struct, Struct, int, Struct]] = {
    b"II*\0": (Struct("<I"), Struct("<H"), 12, Struct("<H")),
    b"MM\0*": (Struct(">I"), Struct(">H"), 12, Struct(">H")),
    b"II+\0": (Struct("<Q"), Struct("<Q"), 20, Struct("<H")),
    b"MM\0+": (Struct(">Q"), Struct(">Q"), 20, Struct(">H")),
}


def _unpack(fh: io.BufferedReader, strct: Struct) -> int:
    return strct.unpack(fh.read(strct.size))[0]


def tiff2xml(path: Path | str) -> bytes:
    """Extract the OME-XML from a TIFF file."""
    with Path(path).open(mode="rb") as fh:
        head = fh.read(4)
        if head not in TIFF_TYPES:  # pragma: no cover
            raise ValueError(f"{path!r} does not have a recognized TIFF header")

        offset_fmt, tagno_fmt, tagsize, codeformat = TIFF_TYPES[head]
        offset_size = offset_fmt.size
        offset_size_4 = offset_size + 4

        if offset_size == 8:
            fh.seek(4, 1)
        fh.seek(_unpack(fh, offset_fmt))
        for _ in range(_unpack(fh, tagno_fmt)):
            tagstruct = fh.read(tagsize)
            if codeformat.unpack(tagstruct[:2])[0] == 270:
                size = offset_fmt.unpack(tagstruct[4:offset_size_4])[0]
                if size <= offset_size:
                    desc = tagstruct[offset_size_4 : offset_size_4 + size]
                    break
                fh.seek(offset_fmt.unpack(tagstruct[-offset_size:])[0])
                desc = fh.read(size)
                break
        else:  # pragma: no cover
            raise ValueError(f"No OME metadata found in file: {path}")
    if desc[-1] == 0:
        desc = desc[:-1]
    return desc
