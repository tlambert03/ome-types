from pydantic import Field

from ome_types._autogenerated.ome_2016_06.reference import Reference

__NAMESPACE__ = "http://www.openmicroscopy.org/Schemas/OME/2016-06"


class ImageRef(Reference):
    """The ImageRef element is a reference to an Image element."""

    class Meta:
        namespace = "http://www.openmicroscopy.org/Schemas/OME/2016-06"

    id: str = Field(
        default="__auto_sequence__",
        pattern=r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Image:\S+)|(Image:\S+)",
        json_schema_extra={
            "name": "ID",
            "type": "Attribute",
            "required": True,
            "pattern": r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Image:\S+)|(Image:\S+)",
        },
    )