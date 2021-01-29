import os
from pathlib import Path
from struct import unpack
from typing import Union

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

try:
    from .model import OME
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "Could not import 'ome_types.model.OME'.\nIf you are in a dev environment, "
        "you may need to run 'python -m src.ome_autogen'"
    ) from None
from .schema import to_dict, to_xml, validate  # isort:skip

__all__ = ["to_dict", "validate", "from_xml", "to_xml", "from_tiff"]


def from_xml(xml: Union[Path, str]) -> OME:  # type: ignore
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
    d = to_dict(xml)
    for key in list(d.keys()):
        if key.startswith(("xml", "xsi")):
            d.pop(key)

    return OME(**d)  # type: ignore


def from_tiff(path: Union[Path, str]) -> OME:
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
    return from_xml(_tiff2xml(path))


def _tiff2xml(path: Union[Path, str]) -> str:
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
    return desc.decode("utf-8")
