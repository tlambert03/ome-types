from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator

from deepdiff import DeepDiff
from fuzzywuzzy import fuzz
from pydantic import BaseModel

import ome_types
from ome_types.model import Reference

if TYPE_CHECKING:
    from types import ModuleType

DOCS = Path(__file__).parent.parent
V1 = Path(__file__).parent / "ome_types_v1.json"
PLURALS = """
    <details>

    <summary>List of plural name changes</summary>
    
    These fields appear in many different classes:

    - `annotation_ref` -> `annotation_refs`
    - `bin_data` -> `bin_data_blocks`
    - `dataset_ref` -> `dataset_refs`
    - `emission_filter_ref` -> `emission_filters`
    - `excitation_filter_ref` -> `excitation_filters`
    - `experimenter_ref` -> `experimenter_refs`
    - `folder_ref` -> `folder_refs`
    - `image_ref` -> `image_refs`
    - `leader` -> `leaders`
    - `light_source_settings` -> `light_source_settings_combinations`
    - `m` -> `ms`
    - `microbeam_manipulation_ref` -> `microbeam_manipulation_refs`
    - `plate_ref` -> `plate_refs`
    - `roi_ref` -> `roi_refs`
    - `well_sample_ref` -> `well_sample_refs`

    </details>
"""

GLOBAL_CHANGES = [
    (
        "All IDs are no longer subclasses of `LSID`, but are now simply `str` type "
        "with a pydantic regex validator."
    ),
    (
        "Many plural names have been updated, such as `annotation_ref` -> "
        "`annotation_refs`. The old names still work in `__init__` methods and as "
        "attributes on instances, but will emit a deprecation warning." + PLURALS
    ),
    (
        "Fields types `PositiveInt`, `PositiveFloat`, `NonNegativeInt`, and "
        "`NonNegativeFloat` are no longer typed with subclasses of pydantic "
        "`ConstrainedInt` and `ConstrainedFloat`, but are now simply `int` or "
        "`float` type with field validators."
    ),
    (
        "Many local `Type` enums have been renamed to globally unique names. "
        "For example `model.detector.Type` is now `model.Detector_Type`. "
        "For backwards compatibility, the old names are still available as aliases "
        "in the corresponding modules.  For example, `Detector_Type` is aliased as "
        "`Type` in the `model.detector` module."
    ),
    (
        "The `kind` fields that were present on `Shape` and `LightSourceGroup` "
        "subclasses have been removed from the models. The `kind` key may still be "
        "included in a `dict` when instantiating a subclass, but the name will not "
        "be available on the model. (This was not an OME field to begin with, it "
        "was a workaround for serialization/deserialization to `dict`.)"
    ),
    (
        "Many fields that take an `Enum` and have a default value have had their types "
        "changed from `Optional[EnumType]` to `EnumType`.  For example fields typed as"
        "`Optional[UnitsLength]` for which a default value is specified are now typed "
        "as `UnitsLength`."
    ),
    (
        "The `ome_types.model.simple_types` module is deprecated and should not "
        "be used (import directly from `model` instead).  Names that were previously "
        "there are still aliased in `simple_types` for backwards compatibility, "
        "but code should be updated and a deprecation warning will soon be added."
    ),
]


def iter_fields(model: type[BaseModel]) -> Iterator[tuple[str, str, str]]:
    for name, field_info in model.__fields__.items():
        # skip fields that are inherited from a parent class
        if any(
            name in getattr(supercls, "__annotations__", {})
            for supercls in model.__mro__[1:]
        ):
            continue
        if issubclass(model, Reference) and name == "id":
            continue
        if name == "kind":
            continue
        yield model.__name__, name, field_info._type_display()
        if isinstance(field_info.type_, type) and issubclass(
            field_info.type_, BaseModel
        ):
            yield from iter_fields(field_info.type_)


def get_fields(module: ModuleType) -> dict[str, Any]:
    types: dict[str, dict[str, str]] = {}

    for name, obj in vars(module).items():
        if isinstance(obj, type) and issubclass(obj, BaseModel) and name not in types:
            types.setdefault(name, {})
            for cls, name, type_ in iter_fields(obj):
                types.setdefault(cls, {})[name] = type_
    return types


def dump_fields() -> None:
    v = 1 if ome_types.__version__ == "unknown" else 2
    types = get_fields(ome_types.model)
    with open(f"ome_types_v{v}.json", "w") as f:
        json.dump(types, f, indent=2, sort_keys=True)


def get_diffs(pth1: Path = V1) -> tuple[list, list, dict, dict]:
    data1 = json.loads(pth1.read_text())
    data2 = get_fields(ome_types.model)
    diff = DeepDiff(data1, data2, ignore_order=True)

    removed = list(diff["dictionary_item_removed"])
    added = list(diff["dictionary_item_added"])
    keys_changed = {}
    for key in list(diff["dictionary_item_removed"]):
        ratios = [fuzz.ratio(key, k) for k in added]
        max_ratio = max(ratios)
        if max_ratio > 85:
            keys_changed[key] = added.pop(ratios.index(max(ratios)))
            removed.remove(key)
    return removed, added, keys_changed, diff.get("values_changed", {})


def _cls_field(key: str) -> tuple[str, str | None]:
    cls_name = key.split("root['", 1)[1].split("']", 1)[0]
    field_name = key.rsplit("']['", 1)[-1].strip("']") if "][" in key else None
    return cls_name, field_name


def gather_classes() -> tuple[dict, dict]:
    keys_removed, keys_added, keys_changed, values_changed = get_diffs()
    module_changes: dict = {"added": [], "removed": []}

    # dict of {ClassName -> {field_name: [changes...]'}}
    class_changes: dict[str, dict[str, dict]] = {}

    for lst, change_type in [(keys_removed, "removed"), (keys_added, "added")]:
        for key in lst:
            cls_name, field_name = _cls_field(key)
            if field_name is None and cls_name != "Value":
                module_changes[change_type].append(cls_name)
            else:
                cls_dict = class_changes.setdefault(cls_name, {})
                cls_dict[field_name] = {"type": f"name_{change_type}"}

    for old_key, new_key in keys_changed.items():
        cls_name, from_field = _cls_field(old_key)
        _, to_field = _cls_field(new_key)
        cls_dict = class_changes.setdefault(cls_name, {})
        cls_dict[from_field] = {"type": "name_changed", "to": to_field}

    for key, value in values_changed.items():
        cls_name, field_name = _cls_field(key)
        old = value["old_value"]
        new = value["new_value"]
        if field_name == "id" and new == "ConstrainedStrValue":
            continue
        if (
            ("PositiveInt" in old and "ConstrainedIntValue" in new)
            or ("PositiveFloat" in old and "ConstrainedFloatValue" in new)
            or ("NonNegativeInt" in old and "ConstrainedIntValue" in new)
            or ("NonNegativeFloat" in old and "ConstrainedFloatValue" in new)
        ):
            continue

        cls_dict = class_changes.setdefault(cls_name, {})
        cls_dict[field_name] = {"type": "type_changed", "from": old, "to": new}

    return class_changes, module_changes


def markdown_changes(heading_level: int = 2) -> str:
    lines: list[str] = []
    hd1 = "#" * heading_level
    hd2 = "#" * (heading_level + 1)
    class_changes, module_changes = gather_classes()

    lines.extend([f"{hd1} General Changes", "", ":eyes: **Read these first**", ""])
    for change in GLOBAL_CHANGES:
        lines.append("- " + change)

    lines.extend(["", f"{hd1} Changes to `ome_types.model`", ""])
    lines.extend(["", f"{hd2} Added classes", ""])
    for added in module_changes["added"]:
        lines.append(f"- [`{added}`][ome_types.model.{added}]")
    lines.extend(["", f"{hd2} Removed classes", ""])
    for removed in module_changes["removed"]:
        lines.append(f"- `{removed}`")

    lines.extend(["", f"{hd1} Class Field Changes", ""])
    for cls_name, cls_changes in class_changes.items():
        # special casing, but don't care to make it more general
        if cls_name == "Value":
            link = "`XMLAnnotation.Value`"
        elif cls_name == "M":
            link = "`Map.M`"
        elif cls_name == "BinaryOnly":
            link = "`OME.BinaryOnly`"
        elif cls_name == "UUID":
            link = "`TiffData.UUID`"
        else:
            link = f"[`{cls_name}`][ome_types.model.{cls_name}]"
        lines.append(f"{hd2} {link}\n")
        for field_name, field_changes in cls_changes.items():
            change_type = field_changes["type"]
            if change_type == "name_removed":
                lines.append(f"- **`{field_name}`** - name removed")
            elif change_type == "name_added":
                lines.append(f"- **`{field_name}`** - name added")
            elif change_type == "name_changed":
                to_field = field_changes["to"]
                lines.append(f"- **`{field_name}`** - name changed to `{to_field}`")
            elif change_type == "type_changed":
                from_type = field_changes["from"]
                to_type = field_changes["to"]
                lines.append(
                    f"- **`{field_name}`** - type changed from "
                    f"`{from_type}` to `{to_type}`"
                )
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    migration = DOCS / "migration.md"
    current_text = migration.read_text()
    START = "<!-- START_GENERATED_MARKDOWN -->"
    END = "<!-- END_GENERATED_MARKDOWN -->"
    start = current_text.index(START)
    end = current_text.index(END)
    md = markdown_changes()
    new_text = current_text[: start + len(START)] + "\n" + md + current_text[end:]
    migration.write_text(new_text)
