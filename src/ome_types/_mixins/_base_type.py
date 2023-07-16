import warnings
from datetime import datetime
from enum import Enum
from textwrap import indent
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    cast,
)

from pydantic import BaseModel

from ome_types._mixins._ids import validate_id
from ome_types._pydantic_compat import (
    PYDANTIC2,
    field_type,
    field_validator,
    model_dump,
    model_fields,
    update_set_fields,
)

try:
    from ome_types.units import add_quantity_properties
except ImportError:
    add_quantity_properties = lambda cls: None  # noqa: E731

if TYPE_CHECKING:
    from pydantic import ConfigDict

    from ome_types._conversion import XMLSource


T = TypeVar("T", bound="OMEType")
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


CONFIG: "ConfigDict" = {
    "arbitrary_types_allowed": True,
    "validate_assignment": True,
    "validate_default": True,
}


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

    if PYDANTIC2:
        model_config = CONFIG
    else:
        Config = type("Config", (), CONFIG)  # type: ignore

    # allow use with weakref
    __slots__: ClassVar[Set[str]] = {"__weakref__"}  # type: ignore

    _vid = field_validator("id", mode="before", always=True, check_fields=False)(
        validate_id
    )

    def __init__(self, **data: Any) -> None:
        warn_extra = data.pop("warn_extra", True)
        field_names = set(model_fields(self))
        _move_deprecated_fields(data, field_names)
        super().__init__(**data)
        kwargs = set(data.keys())
        extra = kwargs - field_names
        if extra and warn_extra:
            warnings.warn(
                f"Unrecognized fields for type {type(self)}: {kwargs - field_names}",
                stacklevel=3,
            )

    def __init_subclass__(cls) -> None:
        """Add `*_quantity` property for fields that have both a value and a unit.

        where `*_quantity` is a pint `Quantity`.
        """
        add_quantity_properties(cls)

    def __repr_args__(self) -> Sequence[Tuple[Optional[str], Any]]:
        """Repr with only set values, and truncated sequences."""
        args = []
        for k, v in model_dump(self, exclude_defaults=True).items():
            if k == "kind":
                continue
            if isinstance(v, Sequence) and not isinstance(v, str):
                if v == []:  # skip empty lists
                    continue
                # if this is a sequence with a long repr, just show the length
                # and type
                if len(repr(v).split(",")) > 5:
                    ftype = field_type(model_fields(self)[k])
                    type_name = getattr(field_type, "__name__", str(ftype))
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

        return super().__getattr__(key)  # type: ignore

    def to_xml(self, **kwargs: Any) -> str:
        """Serialize this object to XML.

        See docstring of [`ome_types.to_xml`][] for kwargs.
        """
        from ome_types._conversion import to_xml

        return to_xml(self, **kwargs)

    @classmethod
    def from_xml(cls: Type[T], xml: "XMLSource", **kwargs: Any) -> T:
        """Read an ome-types class from XML.

        See docstring of [`ome_types.from_xml`][] for kwargs.

        Note: this will return an instance of whatever the top node is in the XML.
        so technically, the return type here could be incorrect.  But when used
        properly (`Image.from_xml()`, `Pixels.from_xml()`, etc.) on an unusual xml
        document it can provide additional typing information.
        """
        from ome_types._conversion import from_xml

        return cast(T, from_xml(xml, **kwargs))

    def _update_set_fields(self) -> None:
        """Update set fields with populated mutable sequences.

        Because pydantic isn't aware of mutations to sequences, it can't tell when
        a field has been "set" by mutating a sequence.  This method updates the
        self.__fields_set__ attribute to reflect that.  We assume that if an attribute
        is not None, and is not equal to the default value, then it has been set.
        """
        update_set_fields(self)


class _RawRepr:
    """Helper class to allow repr to show raw values for fields that are sequences."""

    def __init__(self, raw: str) -> None:
        self.raw = raw

    def __repr__(self) -> str:
        return self.raw
