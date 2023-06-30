import json
from pathlib import Path
from typing import Any, Sequence

from pydantic import BaseModel
from pydantic.typing import display_as_type

import ome_types

TESTS = Path(__file__).parent
KNOWN_CHANGES: dict[str, list[tuple[str, str | None]]] = {
    "OME.datasets": [
        ("annotation_ref", "annotation_refs"),
        ("image_ref", "image_refs"),
    ],
    "OME.experimenter_groups": [
        ("annotation_ref", "annotation_refs"),
        ("experimenter_ref", "experimenter_refs"),
        ("leader", "leaders"),
    ],
    "OME.experimenters": [("annotation_ref", "annotation_refs")],
    "OME.experiments.microbeam_manipulations": [
        ("roi_ref", "roi_refs"),
        ("light_source_settings", "light_source_settings_combinations"),
    ],
    "OME.folders": [
        ("annotation_ref", "annotation_refs"),
        ("folder_ref", "folder_refs"),
        ("image_ref", "image_refs"),
        ("roi_ref", "roi_refs"),
    ],
    "OME.images.pixels": [("bin_data", "bin_data_blocks")],
    "OME.images.pixels.channels": [("annotation_ref", "annotation_refs")],
    "OME.images.pixels.channels.light_path": [
        ("annotation_ref", "annotation_refs"),
        ("emission_filter_ref", "emission_filters"),
        ("excitation_filter_ref", "excitation_filters"),
    ],
    "OME.images.pixels.planes": [("annotation_ref", "annotation_refs")],
    "OME.images": [
        ("annotation_ref", "annotation_refs"),
        ("microbeam_manipulation_ref", "microbeam_manipulation_refs"),
        ("roi_ref", "roi_refs"),
    ],
    "OME.images.imaging_environment.map": [("m", "ms")],
    "OME.instruments": [
        ("annotation_ref", "annotation_refs"),
        ("light_source_group", None),
    ],
    "OME.instruments.detectors": [("annotation_ref", "annotation_refs")],
    "OME.instruments.dichroics": [("annotation_ref", "annotation_refs")],
    "OME.instruments.filter_sets": [
        ("emission_filter_ref", "emission_filters"),
        ("excitation_filter_ref", "excitation_filters"),
    ],
    "OME.instruments.filters": [("annotation_ref", "annotation_refs")],
    "OME.instruments.objectives": [("annotation_ref", "annotation_refs")],
    "OME.plates": [("annotation_ref", "annotation_refs")],
    "OME.plates.plate_acquisitions": [
        ("annotation_ref", "annotation_refs"),
        ("well_sample_ref", "well_sample_refs"),
    ],
    "OME.plates.wells": [("annotation_ref", "annotation_refs")],
    "OME.projects": [
        ("annotation_ref", "annotation_refs"),
        ("dataset_ref", "dataset_refs"),
    ],
    "OME.rois": [("annotation_ref", "annotation_refs")],
    "OME.screens": [("annotation_ref", "annotation_refs"), ("plate_ref", "plate_refs")],
    "OME.screens.reagents": [("annotation_ref", "annotation_refs")],
    # OME.structured_annotations went from
    # List[Annotation] -> Optional[StructuredAnnotations]
    # this is the main breaking change.
    "OME.structured_annotations": [
        ("annotation_ref", None),
        ("id", None),
        ("annotator", None),
        ("description", None),
        ("namespace", None),
    ],
}


def _assert_names_match(
    old: dict[str, Any], new: dict[str, Any], path: Sequence[str] = ()
) -> None:
    """Make sure every key in old is in new, or that it's in KNOWN_CHANGES."""
    for old_key, value in old.items():
        new_key = old_key
        if old_key not in new:
            _path = ".".join(path)
            if _path in KNOWN_CHANGES:
                for from_, new_key in KNOWN_CHANGES[_path]:  # type: ignore
                    if old_key == from_ and (new_key in new or new_key is None):
                        break
                else:
                    raise AssertionError(
                        f"Key {old_key!r} not in new model at {_path}: {list(new)}"
                    )
            else:
                raise AssertionError(f"{_path!r} not in KNOWN_CHANGES")

        if isinstance(value, dict) and new_key in new:
            _assert_names_match(value, new[new_key], (*path, old_key))


def _get_fields(cls: type[BaseModel]) -> dict[str, Any]:
    fields = {}
    for name, field in cls.__fields__.items():
        if name.startswith("_"):
            continue
        if isinstance(field.type_, type) and issubclass(field.type_, BaseModel):
            fields[name] = _get_fields(field.type_)
        else:
            fields[name] = display_as_type(field.outer_type_)  # type: ignore
    return fields


def test_names() -> None:
    with (TESTS / "data" / "old_model.json").open() as f:
        old_names = json.load(f)
    new_names = _get_fields(ome_types.model.OME)
    _assert_names_match(old_names, new_names, ("OME",))
