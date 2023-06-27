from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ome-types2")
except PackageNotFoundError:
    __version__ = "unknown"

from ome_types2._conversion import from_tiff, from_xml, to_dict
from ome_types2.model import OME

__all__ = ["__version__", "OME", "from_xml", "from_tiff", "to_dict"]
