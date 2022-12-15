import os
from pathlib import Path
from typing import Any, Dict, Optional, Union, cast
from warnings import warn

from typing_extensions import Protocol

from .model import OME


class Parser(Protocol):
    # Used for type checks on xml parsers
    def __call__(
        self, path_or_str: Union[Path, str, bytes], validate: Optional[bool] = False
    ) -> Dict[str, Any]:
        ...


def to_dict(
    xml: Union[Path, str, bytes],
    *,
    parser: Union[Parser, str, None] = None,
    validate: Optional[bool] = None,
) -> Dict[str, Any]:
    """Convert OME XML to dict.

    Parameters
    ----------
    xml : Union[Path, str, bytes]
        XML string or path to XML file.
    parser : Union[Parser, str]
        Either a parser callable with signature:
        `(path_or_str: Union[Path, str, bytes], validate: Optional[bool] = False) ->
        Dict`, or a string.  If a string, must be either 'lxml' or 'xmlschema'. by
        default "lxml"
    validate : Optional[bool], optional
        Whether to validate XML as valid OME XML, by default (`None`), the choices is
        left to the parser (which is `False` for the lxml parser)

    Returns
    -------
    Dict[str, Any]
        OME model dict.

    Raises
    ------
    KeyError
        If `parser` is a string, and not one of `'lxml'` or `'xmlschema'`
    """
    if parser is None:
        warn(
            "The default XML parser will be changing from 'xmlschema' to 'lxml' in "
            "version 0.4.0.  To silence this warning, please provide the `parser` "
            "argument, specifying either 'lxml' (to opt into the new behavior), or"
            "'xmlschema' (to retain the old behavior).",
            FutureWarning,
            stacklevel=2,
        )
        parser = "xmlschema"

    if isinstance(parser, str):
        if parser == "lxml":
            from ._lxml import lxml2dict

            parser = cast(Parser, lxml2dict)
        elif parser == "xmlschema":
            from ._xmlschema import xmlschema2dict

            parser = cast(Parser, xmlschema2dict)
        else:
            raise KeyError("parser string must be one of {'lxml', 'xmlschema'}")

    d = parser(xml) if validate is None else parser(xml, validate=validate)
    for key in list(d.keys()):
        if key.startswith(("xml", "xsi")):
            d.pop(key)
    return d


def from_xml(
    xml: Union[Path, str, bytes],
    *,
    parser: Union[Parser, str, None] = None,
    validate: Optional[bool] = None,
) -> OME:
    """Generate OME metadata object from XML string or path.

    Parameters
    ----------
    xml : Union[Path, str, bytes]
        XML string or path to XML file.
    parser : Union[Parser, str]
        Either a parser callable with signature: `(path_or_str: Union[Path, str, bytes],
        validate: Optional[bool] = False) -> Dict`, or a string.  If a string, must be
        either 'lxml' or 'xmlschema'. by default "lxml"
    validate : Optional[bool], optional
        Whether to validate XML as valid OME XML, by default (`None`), the choices is
        left to the parser (which is `False` for the lxml parser)


    Returns
    -------
    ome: ome_types.model.ome.OME
        ome_types.OME metadata object
    """
    d = to_dict(os.fspath(xml), parser=parser, validate=validate)
    return OME(**d)


def from_tiff(
    path: Union[Path, str],
    *,
    parser: Union[Parser, str, None] = None,
    validate: Optional[bool] = True,
) -> OME:
    """Generate OME metadata object from OME-TIFF path.

    This will use the first ImageDescription tag found in the TIFF header.

    Parameters
    ----------
    path : Union[Path, str]
        Path to OME TIFF.
    parser : Union[Parser, str]
        Either a parser callable with signature: `(path_or_str: Union[Path, str, bytes],
        validate: Optional[bool] = False) -> Dict`, or a string.  If a string, must be
        either 'lxml' or 'xmlschema'. by default "lxml"
    validate : Optional[bool], optional
        Whether to validate XML as valid OME XML, by default (`None`), the choices is
        left to the parser (which is `False` for the lxml parser)


    Returns
    -------
    ome: ome_types.model.ome.OME
        ome_types.OME metadata object

    Raises
    ------
    ValueError
        If the TIFF file has no OME metadata.
    """
    return from_xml(_tiff2xml(path), parser=parser, validate=validate)


def _tiff2xml(path: Union[Path, str]) -> bytes:
    """Extract OME XML from OME-TIFF path.

    This will use the first ImageDescription tag found in the TIFF header.

    Parameters
    ----------
    path : Union[Path, str]
        Path to OME TIFF.

    Returns
    -------
    xml : str
        OME XML

    Raises
    ------
    ValueError
        If the TIFF file has no OME metadata.
    """
    from struct import unpack

    with Path(path).open(mode="rb") as fh:
        try:
            offsetsize, offsetformat, tagnosize, tagnoformat, tagsize, codeformat = {
                b"II*\0": (4, "<I", 2, "<H", 12, "<H"),
                b"MM\0*": (4, ">I", 2, ">H", 12, ">H"),
                b"II+\0": (8, "<Q", 8, "<Q", 20, "<H"),
                b"MM\0+": (8, ">Q", 8, ">Q", 20, ">H"),
            }[fh.read(4)]
        except KeyError as e:
            raise ValueError(f"{path!r} does not have a recognized TIFF header") from e

        fh.read(4 if offsetsize == 8 else 0)
        fh.seek(unpack(offsetformat, fh.read(offsetsize))[0])
        for _ in range(unpack(tagnoformat, fh.read(tagnosize))[0]):
            tagstruct = fh.read(tagsize)
            if unpack(codeformat, tagstruct[:2])[0] == 270:
                size = unpack(offsetformat, tagstruct[4 : 4 + offsetsize])[0]
                if size <= offsetsize:
                    desc = tagstruct[4 + offsetsize : 4 + offsetsize + size]
                    break
                fh.seek(unpack(offsetformat, tagstruct[-offsetsize:])[0])
                desc = fh.read(size)
                break
        else:
            raise ValueError(f"No OME metadata found in file: {path}")
    if desc[-1] == 0:
        desc = desc[:-1]
    return desc


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
    from ._xmlschema import to_xml

    return to_xml(ome, **kwargs)


def validate_xml(xml: str, schema: Any = None) -> None:
    from ._xmlschema import validate

    validate(xml, schema=schema)
