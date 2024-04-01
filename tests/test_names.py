from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

import pytest
import some_types
from pydantic import BaseModel, version
from some_types import model

PYDANTIC2 = version.VERSION.startswith("2")
TESTS = Path(__file__).parent
KNOWN_CHANGES: dict[str, list[tuple[str, str | None]]] = {
    "SOME.datasets": [
        ("annotation_ref", "annotation_refs"),
        ("image_ref", "image_refs"),
    ],
    "SOME.experimenter_groups": [
        ("annotation_ref", "annotation_refs"),
        ("experimenter_ref", "experimenter_refs"),
        ("leader", "leaders"),
    ],
    "SOME.experimenters": [("annotation_ref", "annotation_refs")],
    "SOME.experiments.microbeam_manipulations": [
        ("roi_ref", "roi_refs"),
        ("light_source_settings", "light_source_settings_combinations"),
    ],
    "SOME.folders": [
        ("annotation_ref", "annotation_refs"),
        ("folder_ref", "folder_refs"),
        ("image_ref", "image_refs"),
        ("roi_ref", "roi_refs"),
    ],
    "SOME.images.pixels": [("bin_data", "bin_data_blocks")],
    "SOME.images.pixels.channels": [("annotation_ref", "annotation_refs")],
    "SOME.images.pixels.channels.light_path": [
        ("annotation_ref", "annotation_refs"),
        ("emission_filter_ref", "emission_filters"),
        ("excitation_filter_ref", "excitation_filters"),
    ],
    "SOME.images.pixels.planes": [("annotation_ref", "annotation_refs")],
    "SOME.images": [
        ("annotation_ref", "annotation_refs"),
        ("microbeam_manipulation_ref", "microbeam_manipulation_refs"),
        ("roi_ref", "roi_refs"),
    ],
    "SOME.images.imaging_environment.map": [("m", "ms")],
    "SOME.instruments": [
        ("annotation_ref", "annotation_refs"),
        ("light_source_group", None),
    ],
    "SOME.instruments.detectors": [("annotation_ref", "annotation_refs")],
    "SOME.instruments.dichroics": [("annotation_ref", "annotation_refs")],
    "SOME.instruments.filter_sets": [
        ("emission_filter_ref", "emission_filters"),
        ("excitation_filter_ref", "excitation_filters"),
    ],
    "SOME.instruments.filters": [("annotation_ref", "annotation_refs")],
    "SOME.instruments.objectives": [("annotation_ref", "annotation_refs")],
    "SOME.plates": [("annotation_ref", "annotation_refs")],
    "SOME.plates.plate_acquisitions": [
        ("annotation_ref", "annotation_refs"),
        ("well_sample_ref", "well_sample_refs"),
    ],
    "SOME.plates.wells": [("annotation_ref", "annotation_refs")],
    "SOME.projects": [
        ("annotation_ref", "annotation_refs"),
        ("dataset_ref", "dataset_refs"),
    ],
    "SOME.rois": [("annotation_ref", "annotation_refs")],
    "SOME.screens": [
        ("annotation_ref", "annotation_refs"),
        ("plate_ref", "plate_refs"),
    ],
    "SOME.screens.reagents": [("annotation_ref", "annotation_refs")],
    # SOME.structured_annotations went from
    # List[Annotation] -> Optional[StructuredAnnotations]
    # this is the main breaking change.
    "SOME.structured_annotations": [
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
    from pydantic.typing import display_as_type

    fields = {}
    for name, field in cls.__fields__.items():
        if name.startswith("_"):
            continue
        if isinstance(field.type_, type) and issubclass(field.type_, BaseModel):
            fields[name] = _get_fields(field.type_)
        else:
            fields[name] = display_as_type(field.outer_type_)  # type: ignore
    return fields


@pytest.mark.skipif(PYDANTIC2, reason="no need to check pydantic 2")
def test_names() -> None:
    with (TESTS / "data" / "old_model.json").open() as f:
        old_names = json.load(f)
    new_names = _get_fields(some_types.model.SOME)
    _assert_names_match(old_names, new_names, ("SOME",))


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
    ("some", "SOME"),
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


@pytest.mark.parametrize("name,cls_name", V1_EXPORTS)
def test_model_imports(name: str, cls_name: str) -> None:
    from importlib import import_module

    # with pytest.warns(UserWarning, match="Importing submodules from some_types.model"):
    mod = import_module(f"some_types.model.{name}")

    cls = getattr(mod, cls_name)
    assert cls is not None
    real_module = mod = import_module(f"some_types._autogenerated.some_2016_06.{name}")

    # modules and object must have the same id!  This is important for pickle
    assert real_module is mod
    assert getattr(real_module, cls_name) is cls


def test_deprecated_attrs() -> None:
    some = some_types.from_xml(TESTS / "data" / "instrument-units-default.some.xml")
    with pytest.warns(
        match="Attribute 'FilterSet.excitation_filter_ref' is "
        "deprecated, use 'excitation_filters'"
    ):
        ref1 = some.instruments[0].filter_sets[0].excitation_filter_ref
    assert ref1 is some.instruments[0].filter_sets[0].excitation_filters


def test_deprecated_init_args() -> None:
    with pytest.warns(match="Field 'm' is deprecated. Use 'ms' instead"):
        mapann = model.MapAnnotation(
            id="Annotation:3",
            value=model.Map(m=[{"k": "key", "value": "value"}]),  # type: ignore
        )
    assert len(mapann.value.ms) == 1
