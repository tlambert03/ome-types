from __future__ import annotations

import importlib.util
import sys
from importlib.abc import Loader, MetaPathFinder
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

from ome_types._autogenerated.ome_2016_06 import *  # noqa

# these are here mostly to make mypy happy in pre-commit
# even when the model isn't built
from ome_types._autogenerated.ome_2016_06 import OME as OME
from ome_types._autogenerated.ome_2016_06 import Reference as Reference
from ome_types.model._color import Color as Color
from ome_types.model._shape_union import ShapeUnion as ShapeUnion
from ome_types.model._structured_annotations import (
    StructuredAnnotationList as StructuredAnnotationList,
)

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec
    from types import ModuleType

# ---------------------------------------------------------------------
# Below here is logic to allow importing from ome_types._autogenerated.ome_2016_06
# from ome_types.model.* (to preserve backwards compatibility)
# i.e. importing ome_types.model.map will import from
# ome_types._autogenerated.ome_2016_06.map ... and emit a warning


_OME_2016 = Path(__file__).parent.parent / "_autogenerated" / "ome_2016_06"


class OME2016Loader(Loader):
    def __init__(self, fullname: str) -> None:
        submodule = fullname.split(".", 2)[-1]
        file_2016 = (_OME_2016 / submodule.replace(".", "/")).with_suffix(".py")
        module_2016 = fullname.replace(".model.", "._autogenerated.ome_2016_06.", 1)
        if not file_2016.exists():  # pragma: no cover
            raise ImportError(
                f"Cannot find {submodule!r} in ome_types._autogenerated.ome_2016_06"
            )

        # warnings.warn(
        #     "Importing submodules from ome_types.model is deprecated. "
        #     "Please import types directly from ome_types.model instead.",
        #     stacklevel=2,
        # )
        self.fullname = fullname
        self.module_2016 = module_2016

    def create_module(self, spec: ModuleSpec) -> ModuleType | None:
        """Just return the 2016 version."""
        # this will already be in sys.modules because of the star import above
        return sys.modules[self.module_2016]

    def exec_module(self, module: ModuleType) -> None:
        """We never need to exec."""
        pass


# add a sys.meta_path hook to allow import of any modules in
# ome_types._autogenerated.ome_2016_06
class OMEMetaPathFinder(MetaPathFinder):
    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        """Return a module spec to redirect to ome_types._autogenerated.ome_2016_06."""
        if fullname.startswith("ome_types.model."):
            return importlib.util.spec_from_loader(fullname, OME2016Loader(fullname))
        return None


sys.meta_path.append(OMEMetaPathFinder())

from ome_types.model._converters import register_converters  # noqa

register_converters()
del register_converters
