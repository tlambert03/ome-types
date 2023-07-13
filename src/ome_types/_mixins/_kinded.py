from typing import Any, Dict

from pydantic import BaseModel

from ome_types._pydantic_compat import PYDANTIC2

try:
    from pydantic import model_serializer
except ImportError:
    model_serializer = None  # type: ignore


class KindMixin(BaseModel):
    """This mixin adds a `kind` field to the dict output.

    This helps for casting a dict to a specific subclass, when the fields are
    otherwise identical.
    """

    def __init__(self, **data: Any) -> None:
        data.pop("kind", None)
        return super().__init__(**data)

    def dict(self, **kwargs: Any) -> Dict[str, Any]:
        d = super().dict(**kwargs)
        d["kind"] = self.__class__.__name__.lower()
        return d

    if PYDANTIC2:

        @model_serializer(mode="wrap")
        def serialize_root(self, handler, _info) -> Dict:  # type: ignore
            d = handler(self)
            d["kind"] = self.__class__.__name__.lower()
            return d
