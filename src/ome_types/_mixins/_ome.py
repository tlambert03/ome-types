from __future__ import annotations

import weakref
from typing import TYPE_CHECKING, Any, cast

from ._base_type import OMEType

if TYPE_CHECKING:
    from pathlib import Path

    from ome_types.model.ome_2016_06 import OME, Reference


class OMEMixin:
    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._link_refs()

    def _link_refs(self) -> None:
        ids = collect_ids(self)
        for ref in collect_references(self):
            # all reference subclasses do actually have an 'id' field
            # but it's not declared in the base class
            ref._ref = weakref.ref(ids[ref.id])  # type: ignore [attr-defined]

    def __setstate__(self, state: dict[str, Any]) -> None:
        """Support unpickle of our weakref references."""
        super().__setstate__(state)  # type: ignore
        self._link_refs()

    @classmethod
    def from_xml(cls, xml: Path | str) -> OME:
        from ome_types._conversion import from_xml

        return from_xml(xml)

    @classmethod
    def from_tiff(cls, path: Path | str) -> OME:
        from ome_types._conversion import from_tiff

        return from_tiff(path)

    def to_xml(self) -> str:
        from ome_types._conversion import to_xml

        return to_xml(cast("OME", self))


def collect_ids(value: Any) -> dict[str, OMEType]:
    """Return a map of all model objects contained in value, keyed by id.

    Recursively walks all dataclass fields and iterates over lists. The base
    case is when value is neither a dataclass nor a list.
    """
    from ome_types.model import Reference

    ids: dict[str, OMEType] = {}
    if isinstance(value, list):
        for v in value:
            ids.update(collect_ids(v))
    elif isinstance(value, OMEType):
        for f in value.__fields__:
            if f == "id" and not isinstance(value, Reference):
                # We don't need to recurse on the id string, so just record it
                # and move on.
                ids[value.id] = value  # type: ignore
            else:
                ids.update(collect_ids(getattr(value, f)))
    # Do nothing for uninteresting types.
    return ids


def collect_references(value: Any) -> list[Reference]:
    """Return a list of all References contained in value.

    Recursively walks all dataclass fields and iterates over lists. The base
    case is when value is either a Reference object, or an uninteresting type
    that we don't need to inspect further.

    """
    from ome_types.model import Reference

    references: list[Reference] = []
    if isinstance(value, Reference):
        references.append(value)
    elif isinstance(value, list):
        for v in value:
            references.extend(collect_references(v))
    elif isinstance(value, OMEType):
        for f in value.__fields__:
            references.extend(collect_references(getattr(value, f)))
    # Do nothing for uninteresting types
    return references
