from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ome-types2")
except PackageNotFoundError:
    __version__ = "unknown"

from ome_types import model
from ome_types._conversion import from_tiff, from_xml, to_dict, to_xml
from ome_types.model import OME
from ome_types.units import ureg
from ome_types.validation import validate_xml

__all__ = [
    "__version__",
    "from_tiff",
    "from_xml",
    "model",
    "OME",
    "to_dict",
    "to_xml",
    "ureg",
    "validate_xml",
]
