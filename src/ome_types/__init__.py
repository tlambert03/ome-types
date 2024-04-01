from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("some-types")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from some_types.units import ureg  # noqa: TCH004

from some_types import model
from some_types._conversion import from_tiff, from_xml, to_dict, to_xml, validate_xml
from some_types.model import SOME

__all__ = [
    "__version__",
    "from_tiff",
    "from_xml",
    "model",
    "SOME",
    "to_dict",
    "to_xml",
    "ureg",
    "validate_xml",
]


def __getattr__(name: str) -> Any:
    if name == "ureg":
        from some_types.units import ureg

        return ureg
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
