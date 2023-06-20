from typing import Any

from ._ome_2016_06 import simple_types


def __getattr__(name: str) -> Any:
    import warnings

    warnings.warn(
        f"Accessing {name!r} from {__name__!r} is deprecated. "
        f"Use '{__name__}._ome_2016_06.{name}' instead.",
        stacklevel=2,
    )
    return getattr(simple_types, name)
