from typing import Any

from ._units import ureg

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

try:
    from . import model
    from .model import OME
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Could not import 'ome_types.model.OME'.\nIf you are in a dev environment, "
        "you may need to run 'python -m src.ome_autogen'" + str(e)
    ) from None

from ._convenience import (  # isort:skip
    from_tiff,
    from_xml,
    to_dict,
    to_xml,
    validate_xml,
)

__all__ = [
    "from_tiff",
    "from_xml",
    "model",
    "OME",
    "to_dict",
    "to_xml",
    "ureg",
    "validate_xml",
    "__version__",
]


def __getattr__(name: str) -> Any:
    if name == "validate":
        import warnings

        warnings.warn(
            "'ome_types.validate' has been renamed to 'ome_types.validate_xml. "
            "This will raise an exception in the future.",
            FutureWarning,
            stacklevel=2,
        )
        return validate_xml
    raise AttributeError("module {__name__!r} has no attribute {name!r}")
