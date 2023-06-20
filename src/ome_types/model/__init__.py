from __future__ import annotations

import importlib
import sys
from collections.abc import Sequence
from importlib.machinery import ModuleSpec
from importlib.util import spec_from_loader
from typing import TYPE_CHECKING

from ._ome_2016_06 import *  # noqa: F403
from ._ome_2016_06 import _camel_to_snake as _camel_to_snake
from ._ome_2016_06 import _lists as _lists
from ._ome_2016_06 import _plural_to_singular as _plural_to_singular
from ._ome_2016_06 import _singular_to_plural as _singular_to_plural
from ._ome_2016_06 import _snake_to_camel as _snake_to_camel

if TYPE_CHECKING:
    from types import ModuleType


class OMEModuleFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        """An abstract method for finding a spec for the specified module."""
        if fullname.startswith(__name__):
            patched_name = fullname.replace(__name__, f"{__name__}._ome_2016_06")
            loader = sys.modules[patched_name].__loader__
            return spec_from_loader(patched_name, loader)  # type: ignore
        return None


# Register the module loader
sys.meta_path.insert(0, OMEModuleFinder())
