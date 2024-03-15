from typing import TYPE_CHECKING, Any, Dict, Iterator, List, MutableMapping, Optional

try:
    from pydantic import model_serializer
except ImportError:
    model_serializer = None  # type: ignore


if TYPE_CHECKING:
    from typing import Protocol

    from ome_types._autogenerated.ome_2016_06.map import Map

    class HasMsProtocol(Protocol):
        @property
        def ms(self) -> List["Map.M"]: ...


class MapMixin(MutableMapping[str, Optional[str]]):
    def __delitem__(self: "HasMsProtocol", key: str) -> None:
        for m in self.ms:
            if m.k == key:
                self.ms.remove(m)
                return

    def __len__(self: "HasMsProtocol") -> int:
        return len(self.ms)

    def __iter__(self: "HasMsProtocol") -> Iterator[str]:
        yield from (m.k for m in self.ms if m.k is not None)

    def __getitem__(self: "HasMsProtocol", key: str) -> Optional[str]:
        return next((m.value for m in self.ms if m.k == key), None)

    def __setitem__(self: "HasMsProtocol", key: str, value: Optional[str]) -> None:
        for m in self.ms:
            if m.k == key:
                m.value = value or ""
                return
        from ome_types.model import Map

        self.ms.append(Map.M(k=key, value=value))

    def _pydict(self: "HasMsProtocol", **kwargs: Any) -> Dict[str, str]:
        return {m.k: m.value for m in self.ms if m.k is not None}

    def dict(self, **kwargs: Any) -> Dict[str, Any]:
        return self._pydict()  # type: ignore

    if model_serializer is not None:

        @model_serializer(mode="wrap")
        def serialize_root(self, handler, _info) -> dict:  # type: ignore
            return self._pydict()  # type: ignore
