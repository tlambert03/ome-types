# Changes for `ome-types` v0.4.0


## General Changes

- All IDs are no longer subclasses of `LSID`, but are now simply `str` type with a pydantic regex validator.
- Many plural names have been updated, such as `annotation_ref` -> `annotation_refs`. The old names still work in `__init__` methods and as attributes on instances, but will emit a deprecation warning.
- `PositiveInt`, `PositiveFloat`, `NonNegativeInt`, and `NonNegativeFloat` are no longer subclasses of pydantic `ConstrainedInt` and `ConstrainedFloat`, but are now simply `int` or `float` type with field validators.
- Many local `Type` enums have been renamed to globally unique names. For example `model.detector.Type` is now `model.Detector_Type`. For backwards compatibility, the old names are still available as aliases in the corresponding modules.  For example, `Detector_Type` is aliased as `Type` in the `model.detector` module.
- The `kind` fields that were present on many `Shape` or `LightSourceGroup` subclasses have been from the models. The `kind` key may still be included in a `dict` when instantiating a subclass, but the name will not be available on the model. (This was not an OME field to begin with, it was a workaround.)
- Many fields that take an enum and have a default value have had their types changed from `Optional[EnumType]` to `EnumType`.  For example `Optional[UnitsLength]` is now `UnitsLength`.
- The `model.simple_types` module no longer declares anything and should not be used (import directly from `model` instead).  Names that were previously there are still aliased in `simple_types`, but code should be updated.

## `ome_types.model` Module Changes


### Added classes

- `MetadataOnly`
- `ShapeUnion`
- `StructuredAnnotationList`
- `Value`

### Removed classes

- `LightSourceGroup`
- `ShapeGroup`

## Class Field Changes

### `Instrument`

- **`light_source_group`** - name removed
- **`arcs`** - name added
- **`filaments`** - name added
- **`generic_excitation_sources`** - name added
- **`lasers`** - name added
- **`light_emitting_diodes`** - name added
- **`annotation_ref`** - name changed to `annotation_refs`

### `Annotation`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`annotator`** - type changed from `Optional[ExperimenterID]` to `Optional[ConstrainedStrValue]`

### `Channel`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`acquisition_mode`** - type changed from `Optional[AcquisitionMode]` to `Optional[Channel_AcquisitionMode]`
- **`color`** - type changed from `Optional[Color]` to `Color`
- **`contrast_method`** - type changed from `Optional[ContrastMethod]` to `Optional[Channel_ContrastMethod]`
- **`emission_wavelength_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`excitation_wavelength_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`illumination_type`** - type changed from `Optional[IlluminationType]` to `Optional[Channel_IlluminationType]`
- **`pinhole_size_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`

### `Dataset`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`image_ref`** - name changed to `image_refs`

### `Detector`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`type`** - type changed from `Optional[Type]` to `Optional[Detector_Type]`
- **`voltage_unit`** - type changed from `Optional[UnitsElectricPotential]` to `UnitsElectricPotential`

### `Dichroic`

- **`annotation_ref`** - name changed to `annotation_refs`

### `Experimenter`

- **`annotation_ref`** - name changed to `annotation_refs`

### `ExperimenterGroup`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`experimenter_ref`** - name changed to `experimenter_refs`
- **`leader`** - name changed to `leaders`

### `Filter`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`type`** - type changed from `Optional[Type]` to `Optional[Filter_Type]`

### `FilterSet`

- **`emission_filter_ref`** - name changed to `emission_filters`
- **`excitation_filter_ref`** - name changed to `excitation_filters`

### `Folder`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`folder_ref`** - name changed to `folder_refs`
- **`image_ref`** - name changed to `image_refs`
- **`roi_ref`** - name changed to `roi_refs`

### `Image`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`microbeam_manipulation_ref`** - name changed to `microbeam_manipulation_refs`
- **`roi_ref`** - name changed to `roi_refs`

### `LightPath`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`emission_filter_ref`** - name changed to `emission_filters`
- **`excitation_filter_ref`** - name changed to `excitation_filters`

### `LightSource`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`power_unit`** - type changed from `Optional[UnitsPower]` to `UnitsPower`

### `Map`

- **`m`** - name changed to `ms`

### `MicrobeamManipulation`

- **`light_source_settings`** - name changed to `light_source_settings_combinations`
- **`roi_ref`** - name changed to `roi_refs`
- **`type`** - type changed from `List[Type]` to `List[MicrobeamManipulation_value]`

### `Objective`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`correction`** - type changed from `Optional[Correction]` to `Optional[Objective_Correction]`
- **`immersion`** - type changed from `Optional[Immersion]` to `Optional[Objective_Immersion]`
- **`working_distance_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`

### `Pixels`

- **`bin_data`** - name changed to `bin_data_blocks`
- **`dimension_order`** - type changed from `DimensionOrder` to `Pixels_DimensionOrder`
- **`metadata_only`** - type changed from `bool` to `Optional[MetadataOnly]`
- **`physical_size_x_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`physical_size_y_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`physical_size_z_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`time_increment_unit`** - type changed from `Optional[UnitsTime]` to `UnitsTime`

### `Plane`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`delta_t_unit`** - type changed from `Optional[UnitsTime]` to `UnitsTime`
- **`exposure_time_unit`** - type changed from `Optional[UnitsTime]` to `UnitsTime`
- **`hash_sha1`** - type changed from `Optional[Hex40]` to `Optional[bytes]`
- **`position_x_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`position_y_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`position_z_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`

### `Plate`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`well_origin_x_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`well_origin_y_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`

### `PlateAcquisition`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`well_sample_ref`** - name changed to `well_sample_refs`

### `Project`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`dataset_ref`** - name changed to `dataset_refs`

### `ROI`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`union`** - type changed from `List[Union[Rectangle, Mask, Point, Ellipse, Line, Polyline, Polygon, Label]]` to `ShapeUnion`

### `Reagent`

- **`annotation_ref`** - name changed to `annotation_refs`

### `Screen`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`plate_ref`** - name changed to `plate_refs`

### `Shape`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`fill_rule`** - type changed from `Optional[FillRule]` to `Optional[Shape_FillRule]`
- **`font_family`** - type changed from `Optional[FontFamily]` to `Optional[Shape_FontFamily]`
- **`font_size_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`font_style`** - type changed from `Optional[FontStyle]` to `Optional[Shape_FontStyle]`
- **`stroke_width_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`

### `Well`

- **`annotation_ref`** - name changed to `annotation_refs`
- **`color`** - type changed from `Optional[Color]` to `Color`

### `Arc`

- **`type`** - type changed from `Optional[Type]` to `Optional[Arc_Type]`

### `BinData`

- **`compression`** - type changed from `Optional[Compression]` to `BinData_Compression`
- **`length`** - type changed from `int` to `ConstrainedIntValue`
- **`value`** - type changed from `str` to `bytes`

### `BinaryFile`

- **`size`** - type changed from `NonNegativeLong` to `ConstrainedIntValue`

### `BinaryOnly`

- **`uuid`** - type changed from `UniversallyUniqueIdentifier` to `ConstrainedStrValue`

### `DetectorSettings`

- **`read_out_rate_unit`** - type changed from `Optional[UnitsFrequency]` to `UnitsFrequency`
- **`voltage_unit`** - type changed from `Optional[UnitsElectricPotential]` to `UnitsElectricPotential`

### `Experiment`

- **`type`** - type changed from `List[Type]` to `List[Experiment_value]`

### `External`

- **`compression`** - type changed from `Optional[Compression]` to `External_Compression`
- **`sha1`** - type changed from `Hex40` to `bytes`

### `Filament`

- **`type`** - type changed from `Optional[Type]` to `Optional[Filament_Type]`

### `ImagingEnvironment`

- **`air_pressure_unit`** - type changed from `Optional[UnitsPressure]` to `UnitsPressure`
- **`co2_percent`** - type changed from `Optional[PercentFraction]` to `Optional[ConstrainedFloatValue]`
- **`humidity`** - type changed from `Optional[PercentFraction]` to `Optional[ConstrainedFloatValue]`
- **`temperature_unit`** - type changed from `Optional[UnitsTemperature]` to `UnitsTemperature`

### `Laser`

- **`laser_medium`** - type changed from `Optional[LaserMedium]` to `Optional[Laser_LaserMedium]`
- **`pulse`** - type changed from `Optional[Pulse]` to `Optional[Laser_Pulse]`
- **`repetition_rate_unit`** - type changed from `Optional[UnitsFrequency]` to `UnitsFrequency`
- **`type`** - type changed from `Optional[Type]` to `Optional[Laser_Type]`
- **`wavelength_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`

### `LightSourceSettings`

- **`attenuation`** - type changed from `Optional[PercentFraction]` to `Optional[ConstrainedFloatValue]`
- **`wavelength_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`

### `M`

- **`k`** - type changed from `str` to `Optional[str]`

### `Microscope`

- **`type`** - type changed from `Optional[Type]` to `Optional[Microscope_Type]`

### `OME`

- **`structured_annotations`** - type changed from `List[Annotation]` to `StructuredAnnotationList`
- **`uuid`** - type changed from `Optional[UniversallyUniqueIdentifier]` to `Optional[ConstrainedStrValue]`

### `ObjectiveSettings`

- **`medium`** - type changed from `Optional[Medium]` to `Optional[ObjectiveSettings_Medium]`

### `StageLabel`

- **`x_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`y_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`z_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`

### `StructuredAnnotations`

- **`boolean_annotations`** - type changed from `Optional[BooleanAnnotation]` to `List[BooleanAnnotation]`
- **`comment_annotations`** - type changed from `Optional[CommentAnnotation]` to `List[CommentAnnotation]`
- **`double_annotations`** - type changed from `Optional[DoubleAnnotation]` to `List[DoubleAnnotation]`
- **`file_annotations`** - type changed from `Optional[FileAnnotation]` to `List[FileAnnotation]`
- **`list_annotations`** - type changed from `Optional[ListAnnotation]` to `List[ListAnnotation]`
- **`long_annotations`** - type changed from `Optional[LongAnnotation]` to `List[LongAnnotation]`
- **`map_annotations`** - type changed from `Optional[MapAnnotation]` to `List[MapAnnotation]`
- **`tag_annotations`** - type changed from `Optional[TagAnnotation]` to `List[TagAnnotation]`
- **`term_annotations`** - type changed from `Optional[TermAnnotation]` to `List[TermAnnotation]`
- **`timestamp_annotations`** - type changed from `Optional[TimestampAnnotation]` to `List[TimestampAnnotation]`
- **`xml_annotations`** - type changed from `Optional[XMLAnnotation]` to `List[XMLAnnotation]`

### `TransmittanceRange`

- **`cut_in_tolerance_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`cut_in_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`cut_out_tolerance_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`cut_out_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`transmittance`** - type changed from `Optional[PercentFraction]` to `Optional[ConstrainedFloatValue]`

### `UUID`

- **`file_name`** - type changed from `str` to `Optional[str]`
- **`value`** - type changed from `UniversallyUniqueIdentifier` to `ConstrainedStrValue`

### `WellSample`

- **`position_x_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`
- **`position_y_unit`** - type changed from `Optional[UnitsLength]` to `UnitsLength`

### `XMLAnnotation`

- **`value`** - type changed from `Element` to `Value`
