import dataclasses
from typing import Any, Dict, List

from .model.reference import Reference
from .model.simple_types import LSID


def collect_references(value: Any) -> List[Reference]:
    """Return a list of all References contained in value.

    Recursively walks all dataclass fields and iterates over lists. The base
    case is when value is either a Reference object, or an uninteresting type
    that we don't need to inspect further.

    """
    references: List[Reference] = []
    if isinstance(value, Reference):
        references.append(value)
    elif isinstance(value, list):
        for v in value:
            references.extend(collect_references(v))
    elif dataclasses.is_dataclass(value):
        for f in dataclasses.fields(value):
            references.extend(collect_references(getattr(value, f.name)))
    # Do nothing for uninteresting types
    return references


def collect_ids(value: Any) -> Dict[LSID, Any]:
    """Return a map of all model objects contained in value, keyed by id.

    Recursively walks all dataclass fields and iterates over lists. The base
    case is when value is neither a dataclass nor a list.

    """
    ids: Dict[LSID, Any] = {}
    if isinstance(value, list):
        for v in value:
            ids.update(collect_ids(v))
    elif dataclasses.is_dataclass(value):
        for f in dataclasses.fields(value):
            if f.name == "id" and not isinstance(value, Reference):
                # We don't need to recurse on the id string, so just record it
                # and move on.
                ids[value.id] = value
            else:
                ids.update(collect_ids(getattr(value, f.name)))
    # Do nothing for uninteresting types.
    return ids
