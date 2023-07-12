# Migration guide

v0.4.0 was a major release and a complete rewrite of the code-generation
part of the library: `ome-types` is now generated using
[xsdata](https://xsdata.readthedocs.io/en/latest/).

Much effort has been made to keep all existing APIs working, but you may
encounter a number of deprecation warnings. This guide will help you migrate
your code to the new version.


<!-- START_GENERATED_MARKDOWN -->
## General Changes

:eyes: **Read these first**

- All IDs are no longer subclasses of `LSID`, but are now simply `str` type with a pydantic regex validator.
- Many plural names have been updated, such as `annotation_ref` -> `annotation_refs`. The old names still work in `__init__` methods and as attributes on instances, but will emit a deprecation warning.
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

- Fields types `PositiveInt`, `PositiveFloat`, `NonNegativeInt`, and `NonNegativeFloat` are no longer typed with subclasses of pydantic `ConstrainedInt` and `ConstrainedFloat`, but are now simply `int` or `float` type with field validators.
- Many local `Type` enums have been renamed to globally unique names. For example `model.detector.Type` is now `model.Detector_Type`. For backwards compatibility, the old names are still available as aliases in the corresponding modules.  For example, `Detector_Type` is aliased as `Type` in the `model.detector` module.
- The `kind` fields that were present on `Shape` and `LightSourceGroup` subclasses have been removed from the models. The `kind` key may still be included in a `dict` when instantiating a subclass, but the name will not be available on the model. (This was not an OME field to begin with, it was a workaround for serialization/deserialization to `dict`.)
- Many fields that take an `Enum` and have a default value have had their types changed from `Optional[EnumType]` to `EnumType`.  For example fields typed as`Optional[UnitsLength]` for which a default value is specified are now typed as `UnitsLength`.
- The `ome_types.model.simple_types` module is deprecated and should not be used (import directly from `model` instead).  Names that were previously there are still aliased in `simple_types` for backwards compatibility, but code should be updated and a deprecation warning will soon be added.

## Changes to `ome_types.model`


### Added classes

- [`MetadataOnly`][ome_types.model.MetadataOnly]
- [`ShapeUnion`][ome_types.model.ShapeUnion]
- [`StructuredAnnotationList`][ome_types.model.StructuredAnnotationList]

### Removed classes

- `LightSourceGroup`
- `ShapeGroup`

## Class Field Changes

### [`Instrument`][ome_types.model.Instrument]

- **`light_source_group`** - name removed
- **`generic_excitation_sources`** - name added
- **`light_emitting_diodes`** - name added
- **`filaments`** - name added
- **`arcs`** - name added
- **`lasers`** - name added
- **`annotation_ref`** - name changed to `annotation_refs`

### `XMLAnnotation.Value`

- **`None`** - name added

### [`Annotation`][ome_types.model.Annotation]

- **`annotation_ref`** - name changed to `annotation_refs`

### [`Channel`][ome_types.model.Channel]

- **`annotation_ref`** - name changed to `annotation_refs`

### [`LightPath`][ome_types.model.LightPath]

- **`annotation_ref`** - name changed to `annotation_refs`
- **`emission_filter_ref`** - name changed to `emission_filters`
- **`excitation_filter_ref`** - name changed to `excitation_filters`

### [`Dataset`][ome_types.model.Dataset]

- **`annotation_ref`** - name changed to `annotation_refs`
- **`image_ref`** - name changed to `image_refs`

### [`Detector`][ome_types.model.Detector]

- **`annotation_ref`** - name changed to `annotation_refs`

### [`Dichroic`][ome_types.model.Dichroic]

- **`annotation_ref`** - name changed to `annotation_refs`

### [`MicrobeamManipulation`][ome_types.model.MicrobeamManipulation]

- **`light_source_settings`** - name changed to `light_source_settings_combinations`
- **`roi_ref`** - name changed to `roi_refs`

### [`Experimenter`][ome_types.model.Experimenter]

- **`annotation_ref`** - name changed to `annotation_refs`

### [`ExperimenterGroup`][ome_types.model.ExperimenterGroup]

- **`annotation_ref`** - name changed to `annotation_refs`
- **`experimenter_ref`** - name changed to `experimenter_refs`
- **`leader`** - name changed to `leaders`

### [`Filter`][ome_types.model.Filter]

- **`annotation_ref`** - name changed to `annotation_refs`

### [`FilterSet`][ome_types.model.FilterSet]

- **`emission_filter_ref`** - name changed to `emission_filters`
- **`excitation_filter_ref`** - name changed to `excitation_filters`

### [`Folder`][ome_types.model.Folder]

- **`annotation_ref`** - name changed to `annotation_refs`
- **`folder_ref`** - name changed to `folder_refs`
- **`image_ref`** - name changed to `image_refs`
- **`roi_ref`** - name changed to `roi_refs`

### [`Map`][ome_types.model.Map]

- **`m`** - name changed to `ms`

### [`Image`][ome_types.model.Image]

- **`annotation_ref`** - name changed to `annotation_refs`
- **`microbeam_manipulation_ref`** - name changed to `microbeam_manipulation_refs`
- **`roi_ref`** - name changed to `roi_refs`

### [`Pixels`][ome_types.model.Pixels]

- **`bin_data`** - name changed to `bin_data_blocks`

### [`Plane`][ome_types.model.Plane]

- **`annotation_ref`** - name changed to `annotation_refs`

### [`Objective`][ome_types.model.Objective]

- **`annotation_ref`** - name changed to `annotation_refs`

### [`LightSource`][ome_types.model.LightSource]

- **`annotation_ref`** - name changed to `annotation_refs`

### [`Project`][ome_types.model.Project]

- **`annotation_ref`** - name changed to `annotation_refs`
- **`dataset_ref`** - name changed to `dataset_refs`

### [`Plate`][ome_types.model.Plate]

- **`annotation_ref`** - name changed to `annotation_refs`

### [`Well`][ome_types.model.Well]

- **`annotation_ref`** - name changed to `annotation_refs`

### [`PlateAcquisition`][ome_types.model.PlateAcquisition]

- **`annotation_ref`** - name changed to `annotation_refs`
- **`well_sample_ref`** - name changed to `well_sample_refs`

### [`Screen`][ome_types.model.Screen]

- **`annotation_ref`** - name changed to `annotation_refs`
- **`plate_ref`** - name changed to `plate_refs`

### [`Reagent`][ome_types.model.Reagent]

- **`annotation_ref`** - name changed to `annotation_refs`

### [`ROI`][ome_types.model.ROI]

- **`annotation_ref`** - name changed to `annotation_refs`

### [`Shape`][ome_types.model.Shape]

- **`annotation_ref`** - name changed to `annotation_refs`
<!-- END_GENERATED_MARKDOWN -->