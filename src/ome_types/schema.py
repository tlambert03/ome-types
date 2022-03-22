import warnings

from ._xmlschema import *  # noqa

warnings.warn(
    "Direct import from ome_types.schema is deprecated. "
    "Please import convenience functions directly from ome_types. "
    "This will raise an error in the future.",
    FutureWarning,
    stacklevel=2,
)
