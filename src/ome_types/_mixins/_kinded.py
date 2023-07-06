from typing import Any, Dict

from pydantic import BaseModel


class KindMixin(BaseModel):
    def __init__(self, **data: Any) -> None:
        data.pop("kind", None)
        return super().__init__(**data)

    def dict(self, **kwargs: Any) -> Dict[str, Any]:
        d = super().dict(**kwargs)
        d["kind"] = self.__class__.__name__.lower()
        return d
