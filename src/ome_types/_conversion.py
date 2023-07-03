from __future__ import annotations

import operator
import os
from dataclasses import is_dataclass
from pathlib import Path
from struct import Struct
from typing import TYPE_CHECKING, Any, cast

from ome_types.validation import validate_xml

try:
    from lxml import etree as ET
except ImportError:  # pragma: no cover
    from xml.etree import ElementTree as ET

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

    from ome_types.model import OME
    from xsdata_pydantic_basemodel.bindings import XmlContext

    class ParserKwargs(TypedDict, total=False):
        config: ParserConfig
        context: XmlContext
        handler: type[XmlHandler]


OME_2016_06_URI = "http://www.openmicroscopy.org/Schemas/OME/2016-06"
OME_2016_06_NS = f"{{{OME_2016_06_URI}}}OME"


def _get_ome(xml: str | bytes) -> type[OME]:
    if isinstance(xml, str) and not xml.startswith("<"):
        root = ET.parse(xml).getroot()  # noqa: S314
    else:
        root = ET.fromstring(xml)  # noqa: S314

    if root.tag == OME_2016_06_NS:
        from ome_types.model import OME

        return OME
    raise ValueError(f"Unsupported OME schema tag {root.tag}")


def to_dict(source: OME | Path | str | bytes) -> dict[str, Any]:
    if is_dataclass(source):
        raise NotImplementedError("dataclass -> dict is not supported yet")
    return from_xml(  # type: ignore[return-value]
        cast("Path | str | bytes", source),
        # the class_factory is what prevents class instantiation,
        # simply returning the params instead
        parser_kwargs={"config": ParserConfig(class_factory=lambda a, b: b)},
    )


def _class_factory(cls: type, kwargs: Any) -> Any:
    kwargs.setdefault("validation", "strict")
    return cls(**kwargs)


def from_xml(
    xml: Path | str | bytes,
    *,
    validate: bool | None = None,  # TODO implement
    parser: Any = None,  # TODO deprecate
    parser_kwargs: ParserKwargs | None = None,
) -> OME:
    # if validate:
    # raise NotImplementedError("validate=True is not supported yet")

    if isinstance(xml, Path):
        xml = str(xml)

    OME_type = _get_ome(xml)
    parser_kwargs = {"config": ParserConfig(class_factory=_class_factory)}
    _parser = XmlParser(**(parser_kwargs or {}))
    if isinstance(xml, bytes):
        return _parser.from_bytes(xml, OME_type)
    if os.path.isfile(xml):
        return _parser.parse(xml, OME_type)
    return _parser.from_string(xml, OME_type)


def to_xml(
    ome: OME,
    *,
    # exclude_defaults takes precendence over exclude_unset
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
    with Path(path).open(mode="rb") as fh:
        head = fh.read(4)
        if head not in TIFF_TYPES:
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
        else:
            raise ValueError(f"No OME metadata found in file: {path}")
    if desc[-1] == 0:
        desc = desc[:-1]
    return desc
