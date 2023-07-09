import warnings
from datetime import datetime
from enum import Enum
from textwrap import indent
from typing import Any, ClassVar, Dict, Optional, Sequence, Set, Tuple

from pydantic import BaseModel, validator

from ome_types._mixins._ids import validate_id

try:
    from ome_types.units import add_quantity_properties
except ImportError:
    add_quantity_properties = lambda cls: None  # noqa: E731

# Default value to support automatic numbering for id field values.
AUTO_SEQUENCE = "__auto_sequence__"


DEPRECATED_NAMES = {
    "annotation_ref": "annotation_refs",
    "bin_data": "bin_data_blocks",
    "dataset_ref": "dataset_refs",
    "emission_filter_ref": "emission_filters",
    "excitation_filter_ref": "excitation_filters",
    "experimenter_ref": "experimenter_refs",
    "folder_ref": "folder_refs",
    "image_ref": "image_refs",
    "leader": "leaders",
    "light_source_settings": "light_source_settings_combinations",
    "m": "ms",
    "microbeam_manipulation_ref": "microbeam_manipulation_refs",
    "plate_ref": "plate_refs",
    "roi_ref": "roi_refs",
    "well_sample_ref": "well_sample_refs",
}


def _move_deprecated_fields(data: Dict[str, Any], field_names: Set[str]) -> None:
    for key in list(data):
        if (
            key not in field_names
            and key in DEPRECATED_NAMES
            and DEPRECATED_NAMES[key] in field_names
        ):
            warnings.warn(
                f"Field {key!r} is deprecated. Use {DEPRECATED_NAMES[key]!r} instead.",
                stacklevel=2,
            )
            data[DEPRECATED_NAMES[key]] = data.pop(key)


class OMEType(BaseModel):
    """The base class that all OME Types inherit from.

    This provides some global conveniences around auto-setting ids. (i.e., making them
    optional in the class constructor, but never `None` after initialization.).
    It provides a nice `__repr__` that hides things that haven't been changed from
    defaults.  It adds ``*_quantity`` property for fields that have both a value and a
    unit, where `*_quantity` is a [`pint.Quantity`][].  It also provides pickling
    support.
    """

    # pydantic BaseModel configuration.
    # see: https://pydantic-docs.helpmanual.io/usage/model_config/
    class Config:
        arbitrary_types_allowed = False
        validate_assignment = True
        underscore_attrs_are_private = True
        use_enum_values = False
        validate_all = True

    # allow use with weakref
    __slots__: ClassVar[Set[str]] = {"__weakref__"}  # type: ignore

    _v = validator("id", pre=True, always=True, check_fields=False)(validate_id)

    def __init__(self, **data: Any) -> None:
        field_names = set(self.__fields__.keys())
        _move_deprecated_fields(data, field_names)
        super().__init__(**data)
        kwargs = set(data.keys())
        if kwargs - field_names:
            warnings.warn(
                f"Unrecognized fields for type {type(self)}: {kwargs - field_names}",
                stacklevel=2,
            )

    def __init_subclass__(cls) -> None:
        """Add `*_quantity` property for fields that have both a value and a unit.

        where `*_quantity` is a pint `Quantity`.
        """
        add_quantity_properties(cls)

    def __repr_args__(self) -> Sequence[Tuple[Optional[str], Any]]:
        """Repr with only set values, and truncated sequences."""
        args = []
        for k, v in self._iter(exclude_defaults=True):
            if isinstance(v, Sequence) and not isinstance(v, str):
                if v == []:  # skip empty lists
                    continue
                # if this is a sequence with a long repr, just show the length
                # and type
                if len(repr(v).split(",")) > 5:
                    type_name = self.__fields__[k].type_.__name__
                    v = _RawRepr(f"[<{len(v)} {type_name}>]")
            elif isinstance(v, Enum):
                v = v.value
            elif isinstance(v, datetime):
                v = v.isoformat()
            args.append((k, v))
        return sorted(args, key=lambda f: f[0] not in ("name", "id"))

    def __repr__(self) -> str:
        lines = [f"{key}={val!r}," for key, val in self.__repr_args__()]
        if len(lines) == 1:
            body = lines[-1].rstrip(",")
        elif lines:
            body = "\n" + indent("\n".join(lines), "   ") + "\n"
        else:
            body = ""
        return f"{self.__class__.__qualname__}({body})"

    def __getattr__(self, key: str) -> Any:
        """Getattr that redirects deprecated names."""
        cls_name = self.__class__.__name__
        if key in DEPRECATED_NAMES and hasattr(self, DEPRECATED_NAMES[key]):
            new_key = DEPRECATED_NAMES[key]
            warnings.warn(
                f"Attribute '{cls_name}.{key}' is deprecated, use {new_key!r} instead",
                DeprecationWarning,
                stacklevel=2,
            )
            return getattr(self, new_key)
        raise AttributeError(f"{cls_name} object has no attribute {key!r}")


class _RawRepr:
    """Helper class to allow repr to show raw values for fields that are sequences."""

    def __init__(self, raw: str) -> None:
        self.raw = raw

    def __repr__(self) -> str:
        return self.raw
