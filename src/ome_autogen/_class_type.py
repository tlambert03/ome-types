from typing import Any

from pydantic import BaseModel
from xsdata_pydantic.compat import Pydantic


class OME(Pydantic):
    def is_model(self, obj: Any) -> bool:
        clazz = obj if isinstance(obj, type) else type(obj)
        if isinstance(clazz, BaseModel):
            clazz.update_forward_refs()
            return True

        return False



