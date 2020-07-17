try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

import os
from .schema import to_dict, validate

__all__ = ["to_dict", "validate", "from_xml"]


try:
    from .model import OME
except ImportError:
    print("OME dataclasses not found ... running autogeneration")
    import runpy

    runpy.run_module("ome_autogen", run_name="__main__")
    from .model import OME


def from_xml(xml, OME=OME) -> OME:

    xml = os.fspath(xml)
    d = to_dict(xml)
    for key in list(d.keys()):
        if key.startswith(("xml", "xsi")):
            d.pop(key)

    return OME(**d)
