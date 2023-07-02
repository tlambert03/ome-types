"""xsdata pydantic plugin using BaseModel."""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("xsdata-pydantic-basemodel")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "uninstalled"

__author__ = "Talley Lambert"
__email__ = "talley.lambert@gmail.com"
