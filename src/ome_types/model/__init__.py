from __future__ import annotations

import importlib.util
import sys
from importlib.abc import MetaPathFinder
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

from ome_types.model.ome_2016_06 import *  # noqa

# these are here mostly to make mypy happy in pre-commit even when the model isn't built
from ome_types.model.ome_2016_06 import OME as OME
from ome_types.model.ome_2016_06 import Reference as Reference

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec
    from types import ModuleType

_OME_2016 = Path(__file__).parent / "ome_2016_06"


# add a sys.meta_path hook to allow import of any modules in
# ome_types.model.ome_2016_06
class OMEMetaPathFinder(MetaPathFinder):
    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        """Return a module spec for any module in ome_types.model.ome_2016_06."""
        if fullname.startswith("ome_types.model."):
            submodule = fullname.split(".", 2)[-1]
            file_2016 = (_OME_2016 / submodule.replace(".", "/")).with_suffix(".py")
            if file_2016.is_file():
                import warnings

                warnings.warn(
                    "Importing sumodules from ome_types.model is deprecated. "
                    "Please import types directly from ome_types.model instead.",
                    stacklevel=2,
                )
                module_2016 = fullname.replace(".model.", ".model.ome_2016_06.", 1)
                return importlib.util.spec_from_file_location(module_2016, file_2016)
        return None


sys.meta_path.append(OMEMetaPathFinder())
