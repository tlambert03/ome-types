import warnings
from datetime import datetime
from enum import Enum
from textwrap import indent
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Sequence, Set, cast

from pydantic import BaseModel, validator

from ome_types._mixins._ids import validate_id
from ome_types.units import ureg

if TYPE_CHECKING:
    import pint


# Default value to support automatic numbering for id field values.
AUTO_SEQUENCE = "__auto_sequence__"


_UNIT_FIELD = "{}_unit"
_QUANTITY_FIELD = "{}_quantity"
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


class OMEType(BaseModel):
    """The base class that all OME Types inherit from.

    This provides some global conveniences around auto-setting ids. (i.e., making them
    optional in the class constructor, but never ``None`` after initialization.).
    It provides a nice __repr__ that hides things that haven't been changed from
    defaults.  It adds ``*_quantity`` property for fields that have both a value and a
    unit, where ``*_quantity`` is a pint ``Quantity``.  It also provides pickling
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

    def __init__(__pydantic_self__, **data: Any) -> None:
        if "id" in __pydantic_self__.__fields__:
            data.setdefault("id", AUTO_SEQUENCE)
        super().__init__(**data)

    def __init_subclass__(cls) -> None:
        """Add `*_quantity` property for fields that have both a value and a unit.

        where `*_quantity` is a pint `Quantity`.
        """
        for field in cls.__fields__:
            if _UNIT_FIELD.format(field) in cls.__fields__:
                setattr(cls, _QUANTITY_FIELD.format(field), _quantity_property(field))

    def __repr__(self) -> str:
        name = self.__class__.__qualname__
        lines = []
        for f in sorted(
            self.__fields__.values(), key=lambda f: f.name not in ("name", "id")
        ):
            if f.name.endswith("_"):
                continue  # pragma: no cover
            # https://github.com/python/mypy/issues/6910
            default = f.default_factory() if f.default_factory else f.default
            current = getattr(self, f.name)
            if current != default:
                if isinstance(current, Sequence) and not isinstance(current, str):
                    rep = f"[<{len(current)} {f.name.title()}>]"
                elif isinstance(current, Enum):
                    rep = repr(current.value)
                elif isinstance(current, datetime):
                    rep = f"datetime.fromisoformat({current.isoformat()!r})"
                else:
                    rep = repr(current)
                lines.append(f"{f.name}={rep},")
        if len(lines) == 1:
            body = lines[-1].rstrip(",")
        elif lines:
            body = "\n" + indent("\n".join(lines), "   ") + "\n"
        else:
            body = ""
        return f"{name}({body})"

    _v = validator("id", pre=True, always=True, check_fields=False)(validate_id)

    def __getattr__(self, key: str) -> Any:
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


def _quantity_property(field_name: str) -> property:
    """Create property that returns a ``pint.Quantity`` combining value and unit."""

    def quantity(self: Any) -> Optional["pint.Quantity"]:
        value = getattr(self, field_name)
        if value is None:
            return None

        unit = cast("Enum", getattr(self, _UNIT_FIELD.format(field_name)))
        return ureg.Quantity(value, unit.value.replace(" ", "_"))

    return property(quantity)
