from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ome-types2")
except PackageNotFoundError:
    __version__ = "unknown"

from ome_types._conversion import from_tiff, from_xml, to_dict, to_xml
from ome_types.model import OME

__all__ = ["__version__", "OME", "from_xml", "from_tiff", "to_dict", "to_xml"]
