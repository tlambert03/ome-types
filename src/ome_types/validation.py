from __future__ import annotations

import io
import os
from contextlib import suppress
from functools import lru_cache
from pathlib import Path
from typing import IO, TYPE_CHECKING, Union

if TYPE_CHECKING:
    import xmlschema

    XMLSourceType = Union[str, bytes, Path, IO[str], IO[bytes]]

NS_OME = r"{http://www.openmicroscopy.org/Schemas/OME/2016-06}"
OME_2016_06_XSD = str(Path(__file__).parent / "ome-2016-06.xsd")


class ValidationError(ValueError):
    ...


def validate_xml(xml: XMLSourceType, schema: Path | str | None = None) -> None:
    """Validate XML against an XML Schema.

    By default, will validate against the OME 2016-06 schema.
    """
    with suppress(ImportError):
        return validate_xml_with_lxml(xml, schema)

    with suppress(ImportError):  # pragma: no cover
        return validate_xml_with_xmlschema(xml, schema)

    raise ImportError(  # pragma: no cover
        "Validation requires either `lxml` or `xmlschema`. "
        "Please pip install one of them."
    ) from None


def validate_xml_with_lxml(
    xml: XMLSourceType, schema: Path | str | None = None
) -> None:
    """Validate XML against an XML Schema using lxml."""
    from lxml import etree

    tree = etree.parse(schema or OME_2016_06_XSD)  # noqa: S320
    xmlschema = etree.XMLSchema(tree)

    if isinstance(xml, (str, bytes)) and not os.path.isfile(xml):
        xml = io.BytesIO(xml.encode("utf-8") if isinstance(xml, str) else xml)
        doc = etree.parse(xml)  # noqa: S320
    else:
        doc = etree.parse(xml)  # noqa: S320

    if not xmlschema.validate(doc):
        msg = f"Validation of {str(xml)[:20]!r} failed:"
        for error in xmlschema.error_log:
            msg += f"\n  - line {error.line}: {error.message}"
        raise ValidationError(msg)


def validate_xml_with_xmlschema(
    xml: XMLSourceType, schema: Path | str | None = None
) -> None:
    """Validate XML against an XML Schema using xmlschema."""
    from xmlschema.exceptions import XMLSchemaException

    xmlschema = _get_XMLSchema(schema or OME_2016_06_XSD)
    try:
        xmlschema.validate(xml)
    except XMLSchemaException as e:
        raise ValidationError(str(e)) from None


@lru_cache(maxsize=None)
def _get_XMLSchema(schema: Path | str) -> xmlschema.XMLSchema:
    import xmlschema

    xml_schema = xmlschema.XMLSchema(schema)
    # FIXME Hack to work around xmlschema poor support for keyrefs to
    # substitution groups
    ls_sgs = xml_schema.maps.substitution_groups[f"{NS_OME}LightSourceGroup"]
    ls_id_maps = xml_schema.maps.identities[f"{NS_OME}LightSourceIDKey"]
    ls_id_maps.elements = {e: None for e in ls_sgs}
    return xml_schema
