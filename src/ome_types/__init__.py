import os
from pathlib import Path
from typing import Union

from .schema import to_dict, validate

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

__all__ = ["to_dict", "validate", "from_xml"]


def from_xml(xml: Union[Path, str]) -> OME:  # type: ignore
    xml = os.fspath(xml)
    d = to_dict(xml)
    for key in list(d.keys()):
        if key.startswith(("xml", "xsi")):
            d.pop(key)

    return OME(**d)  # type: ignore
