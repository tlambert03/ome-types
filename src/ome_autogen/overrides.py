from typing import NamedTuple, Sequence

# from ome_types._mixins._base_type import AUTO_SEQUENCE
# avoiding import to avoid build-time dependency on the ome-types package
AUTO_SEQUENCE = "__auto_sequence__"


class D(NamedTuple):
    """Thing."""

    # additional lines to add to generated classes
    # Note: imports for these methods must be added to the IMPORT_PATTERNS elswhere.
    add_lines: Sequence[str] = ()
    # when this name is found in the XSD, the type will be overridden with this
    # e.g. "Color" -> "ome_types.model._color.Color"
    type_override: tuple[str, str] | None = None
    never_optional: bool = False
    default: str | None = None
    default_factory: str = ""


OVERRIDES: dict[str, D] = {
    "ID": D(default=repr(AUTO_SEQUENCE)),
    "Union": D(never_optional=True, default_factory="lambda: ROI.Union()"),
    "StructuredAnnotations": D(
        never_optional=True, default_factory="StructuredAnnotations"
    ),
    "FillColor": D(type_override=("ome_types.model._color", "Color")),
    "StrokeColor": D(
        type_override=("ome_types.model._color", "Color"),
    ),
    "Color": D(
        type_override=("ome_types.model._color", "Color"),
        default_factory="Color",
    ),
    "BinData": D(
        add_lines=[
            "_vbindata = model_validator(mode='before')(bin_data_root_validator)"
        ],
    ),
    "Value": D(
        add_lines=["_vany = field_validator('any_elements')(any_elements_validator)"],
    ),
    "Pixels": D(
        add_lines=["_vpix = model_validator(mode='before')(pixels_root_validator)"],
    ),
    "XMLAnnotation": D(
        add_lines=[
            "_vval = field_validator('value', mode='before')(xml_value_validator)"
        ],
    ),
    "PixelType": D(add_lines=["numpy_dtype = property(pixel_type_to_numpy_dtype)"]),
    "OME": D(
        add_lines=[
            "_v_structured_annotations = field_validator('structured_annotations', mode='before')(validate_structured_annotations)"  # noqa: E501
        ],
    ),
    "ROI": D(
        add_lines=[
            "_v_shape_union = field_validator('union', mode='before')(validate_shape_union)"  # noqa: E501
        ],
    ),
    "Map": D(
        add_lines=[
            "_v_map = model_validator(mode='before')(validate_map_annotation)",
            "dict: ClassVar = MapMixin._pydict",
            "__iter__: ClassVar = MapMixin.__iter__",
        ],
    ),
}
