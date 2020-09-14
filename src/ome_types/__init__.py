import os
from pathlib import Path
from typing import Union

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

try:
    from .model import OME
except ImportError:
    raise ImportError(
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
    ome: ome_types.OME
        ome_types.OME metadata object
    """
    xml = os.fspath(xml)
    d = to_dict(xml)
    for key in list(d.keys()):
        if key.startswith(("xml", "xsi")):
            d.pop(key)

    return OME(**d)  # type: ignore


def from_tiff(path: Union[Path, str]) -> OME:
    """Generate OME metadata object from OME TIFF.

    Requires tifffile.

    Parameters
    ----------
    path : Union[Path, str]
        Path to OME TIFF.

    Returns
    -------
    ome: ome_types.OME
        ome_types.OME metadata object

    Raises
    ------
    ImportError
        If `tifffile` is not installed
    ValueError
        If the TIFF file has no OME metadata.
    """
    try:
        import tifffile
    except ImportError:
        raise ImportError(
            "Please `pip install tifffile` to extract OME metadata from a TIFF."
        ) from None

    with tifffile.TiffFile(os.fspath(path)) as tf:
        if not tf.ome_metadata:
            raise ValueError(f"No OME metadata found in {path}")
        return from_xml(tf.ome_metadata)
