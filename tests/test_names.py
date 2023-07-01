from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

import pytest
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


V1_EXPORTS = [
    ("affine_transform", "AffineTransform"),
    ("annotation", "Annotation"),
    ("annotation_ref", "AnnotationRef"),
    ("arc", "Arc"),
    ("basic_annotation", "BasicAnnotation"),
    ("bin_data", "BinData"),
    ("binary_file", "BinaryFile"),
    ("boolean_annotation", "BooleanAnnotation"),
    ("channel", "Channel"),
    ("channel_ref", "ChannelRef"),
    ("comment_annotation", "CommentAnnotation"),
    ("dataset", "Dataset"),
    ("dataset_ref", "DatasetRef"),
    ("detector", "Detector"),
    ("detector_settings", "DetectorSettings"),
    ("dichroic", "Dichroic"),
    ("dichroic_ref", "DichroicRef"),
    ("double_annotation", "DoubleAnnotation"),
    ("ellipse", "Ellipse"),
    ("experiment", "Experiment"),
    ("experiment_ref", "ExperimentRef"),
    ("experimenter", "Experimenter"),
    ("experimenter_group", "ExperimenterGroup"),
    ("experimenter_group_ref", "ExperimenterGroupRef"),
    ("experimenter_ref", "ExperimenterRef"),
    ("external", "External"),
    ("filament", "Filament"),
    ("file_annotation", "FileAnnotation"),
    ("filter", "Filter"),
    ("filter_ref", "FilterRef"),
    ("filter_set", "FilterSet"),
    ("filter_set_ref", "FilterSetRef"),
    ("folder", "Folder"),
    ("folder_ref", "FolderRef"),
    ("generic_excitation_source", "GenericExcitationSource"),
    ("image", "Image"),
    ("image_ref", "ImageRef"),
    ("imaging_environment", "ImagingEnvironment"),
    ("instrument", "Instrument"),
    ("instrument_ref", "InstrumentRef"),
    ("label", "Label"),
    ("laser", "Laser"),
    ("leader", "Leader"),
    ("light_emitting_diode", "LightEmittingDiode"),
    ("light_path", "LightPath"),
    ("light_source", "LightSource"),
    # ("light_source_group", "LightSourceGroup"),
    ("light_source_settings", "LightSourceSettings"),
    ("line", "Line"),
    ("list_annotation", "ListAnnotation"),
    ("long_annotation", "LongAnnotation"),
    ("manufacturer_spec", "ManufacturerSpec"),
    ("map", "Map"),
    ("map_annotation", "MapAnnotation"),
    ("mask", "Mask"),
    ("microbeam_manipulation", "MicrobeamManipulation"),
    ("microbeam_manipulation_ref", "MicrobeamManipulationRef"),
    ("microscope", "Microscope"),
    ("numeric_annotation", "NumericAnnotation"),
    ("objective", "Objective"),
    ("objective_settings", "ObjectiveSettings"),
    ("ome", "OME"),
    ("pixels", "Pixels"),
    ("plane", "Plane"),
    ("plate", "Plate"),
    ("plate_acquisition", "PlateAcquisition"),
    ("point", "Point"),
    ("polygon", "Polygon"),
    ("polyline", "Polyline"),
    ("project", "Project"),
    ("project_ref", "ProjectRef"),
    ("pump", "Pump"),
    ("reagent", "Reagent"),
    ("reagent_ref", "ReagentRef"),
    ("rectangle", "Rectangle"),
    ("reference", "Reference"),
    ("rights", "Rights"),
    ("roi", "ROI"),
    ("roi_ref", "ROIRef"),
    ("screen", "Screen"),
    ("settings", "Settings"),
    ("shape", "Shape"),
    # ("shape_group", "ShapeGroup"),
    ("stage_label", "StageLabel"),
    ("structured_annotations", "StructuredAnnotations"),
    ("tag_annotation", "TagAnnotation"),
    ("term_annotation", "TermAnnotation"),
    ("text_annotation", "TextAnnotation"),
    ("tiff_data", "TiffData"),
    ("timestamp_annotation", "TimestampAnnotation"),
    ("transmittance_range", "TransmittanceRange"),
    ("type_annotation", "TypeAnnotation"),
    ("well", "Well"),
    ("well_sample", "WellSample"),
    ("well_sample_ref", "WellSampleRef"),
    ("xml_annotation", "XMLAnnotation"),
]


@pytest.mark.parametrize("name,cls", V1_EXPORTS)
def test_model_imports(name: str, cls: str) -> None:
    from importlib import import_module

    with pytest.warns(UserWarning, match="Importing sumodules from ome_types.model"):
        mod = import_module(f"ome_types.model.{name}")
    assert getattr(mod, cls) is not None
