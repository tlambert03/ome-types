"""These validators are added to the generated classes in ome_types._autogenerated.

that logic is in the `methods` method in ome_autogen/_generator.py
"""
import warnings
from typing import TYPE_CHECKING, Any, Dict, List, Sequence

if TYPE_CHECKING:
    from ome_types.model import (  # type: ignore
        OME,
        BinData,
        Pixels,
        PixelType,
        StructuredAnnotations,
        XMLAnnotation,
    )
    from xsdata_pydantic_basemodel.compat import AnyElement


# @root_validator(pre=True)
def bin_data_root_validator(cls: "BinData", values: dict) -> Dict[str, Any]:
    # This catches the case of <BinData Length="0"/>, where the parser may have
    # omitted value from the dict, and sets value to b""
    # seems like it could be done in a default_factory, but that would
    # require more modification of xsdata I think
    if "value" not in values:
        if values.get("length") != 0:  # pragma: no cover
            warnings.warn(
                "BinData length is non-zero but value is missing", stacklevel=2
            )
        values["value"] = b""
    return values


# @root_validator(pre=True)
def pixels_root_validator(cls: "Pixels", value: dict) -> dict:
    if "metadata_only" in value:
        if isinstance(value["metadata_only"], bool):
            if not value["metadata_only"]:
                value.pop("metadata_only")
            else:
                # type ignore in case the autogeneration hasn't been built
                from ome_types.model import MetadataOnly  # type: ignore

                value["metadata_only"] = MetadataOnly()

    return value


# @validator("any_elements")
def any_elements_validator(
    cls: "XMLAnnotation.Value", v: List[Any]
) -> List["AnyElement"]:
    # This validator is used because XMLAnnotation.Value.any_elements is
    # annotated as List[object]. So pydantic won't coerce dicts to AnyElement
    # automatically (which is important when constructing OME objects from dicts)
    if not isinstance(v, Sequence):
        raise ValueError(f"any_elements must be a sequence, not {type(v)}")
    # this needs to be delayed until runtime because of circular imports
    from xsdata_pydantic_basemodel.compat import AnyElement

    return [AnyElement(**v) if isinstance(v, dict) else v for v in v]


# @validator('value', pre=True)
def xml_value_validator(cls: "XMLAnnotation", v: Any) -> "XMLAnnotation.Value":
    if isinstance(v, str):
        # FIXME: this is a hack to support passing a string to XMLAnnotation.value
        # there must be a more direct way to do this...
        # (the type ignores here are because the model might not be built yet)
        from ome_types._conversion import OME_2016_06_URI
        from ome_types.model import XMLAnnotation  # type: ignore
        from xsdata_pydantic_basemodel.bindings import XmlParser

        template = '<XMLAnnotation xmlns="{}"><Value>{}</Value></XMLAnnotation>'
        xml = template.format(OME_2016_06_URI, v)
        return XmlParser().from_string(xml, XMLAnnotation).value  # type: ignore
    return v


def pixel_type_to_numpy_dtype(self: "PixelType") -> str:
    """Get a numpy dtype string for this pixel type."""
    m = {
        "float": "float32",
        "double": "float64",
        "complex": "complex64",
        "double-complex": "complex128",
        "bit": "bool",  # ?
    }
    return m.get(self.value, self.value)


# @field_validator("structured_annotations", mode="before")
def validate_structured_annotations(cls: "OME", v: Any) -> "StructuredAnnotations":
    """Convert list input for OME.structured_annotations to dict."""
    from ome_types.model import StructuredAnnotations

    if isinstance(v, StructuredAnnotations):
        return v
    if isinstance(v, list):
        # convert list[AnnotationType] to dict with keys matching the
        # fields in StructuredAnnotations
        _values: dict = {}
        for item in v:
            _values.setdefault(StructuredAnnotations._field_name(item), []).append(item)
        v = _values
    return v
