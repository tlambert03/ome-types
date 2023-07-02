from __future__ import annotations

import os
from dataclasses import is_dataclass
from pathlib import Path
from struct import Struct
from typing import TYPE_CHECKING, Any, cast
from xml.etree import ElementTree as ET

from xsdata.formats.dataclass.parsers.config import ParserConfig
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata_pydantic_basemodel.bindings import XmlParser, XmlSerializer

if TYPE_CHECKING:
    import io
    from typing import TypedDict

    from xsdata.formats.dataclass.parsers.mixins import XmlHandler
    from xsdata_pydantic_basemodel.bindings import XmlContext

    from ome_types.model import OME

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
    ignore_defaults: bool = True,
    indent: int = 2,
    include_schema_location: bool = True,
) -> str:
    config = SerializerConfig(
        pretty_print=indent > 0,
        pretty_print_indent=" " * indent,
        ignore_default_attributes=ignore_defaults,
    )
    if include_schema_location:
        config.schema_location = f"{OME_2016_06_URI} {OME_2016_06_URI}/ome.xsd"

    serializer = XmlSerializer(config=config)
    xml = serializer.render(ome, ns_map={None: OME_2016_06_URI})
    # HACK: xsdata is always including <StructuredAnnotations/> because...
    # 1. we override the default for OME.structured_annotations so that
    #    it's always a present (if empty) list.  That was the v1 behavior
    #    and it allows ome.structured_annotations.append(...) to always work.
    # 2. xsdata thinks it's not nillable, and therefore always includes it
    # ... we might be able to do it better, but this fixes it for now.
    return xml.replace("<StructuredAnnotations/>", "")


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
