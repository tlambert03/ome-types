import warnings
from typing import Any, Dict

from pydantic import root_validator

from ome_types._mixins._base_type import OMEType


class BinDataMixin(OMEType):
    @root_validator(pre=True)
    def _v(cls, values: dict) -> Dict[str, Any]:
        # This catches the case of <BinData Length="0"/>, where the parser may have
        # omitted value from the dict, and sets value to b""
        # seems like it could be done in a default_factory, but that would
        # require more modification of xsdata I think
        if "value" not in values:
            if values.get("length") != 0:
                warnings.warn(
                    "BinData length is non-zero but value is missing", stacklevel=2
                )
            values["value"] = b""
        return values
