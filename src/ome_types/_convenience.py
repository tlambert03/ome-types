import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from typing_extensions import Protocol

from .model import OME
from .util import lxml2dict


class Parser(Protocol):
    # Used for type checks on xml parsers
    def __call__(
        self, path_or_str: Union[Path, str, bytes], validate: Optional[bool] = False
    ) -> Dict[str, Any]:
        ...


def from_xml(
    xml: Union[Path, str, bytes],
    parser: Parser = lxml2dict,
    validate: Optional[bool] = None,
) -> OME:  # type: ignore
    """Generate OME metadata object from XML string or path.

    Parameters
    ----------
    xml : Union[Path, str]
        Path to an XML file, or literal XML string.

    Returns
    -------
    ome: ome_types.model.ome.OME
        ome_types.OME metadata object
    """
    xml = os.fspath(xml)

    if validate is None:
        # Use the default validation preference of the parser
        d = parser(xml)
    else:
        d = parser(xml, validate=validate)

    for key in list(d.keys()):
        if key.startswith(("xml", "xsi")):
            d.pop(key)

    return OME(**d)  # type: ignore


def from_tiff(
    path: Union[Path, str],
    parser: Parser = lxml2dict,
    validate: Optional[bool] = True,
) -> OME:
    """Generate OME metadata object from OME-TIFF path.

    This will use the first ImageDescription tag found in the TIFF header.

    Parameters
    ----------
    path : Union[Path, str]
        Path to OME TIFF.

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
        except KeyError:
            raise ValueError(f"{path!r} does not have a recognized TIFF header")

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
