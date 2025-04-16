from pydantic import Field

from ome_types._autogenerated.ome_2016_06.reference import Reference

__NAMESPACE__ = "http://www.openmicroscopy.org/Schemas/OME/2016-06"


class ROIRef(Reference):
    class Meta:
        namespace = "http://www.openmicroscopy.org/Schemas/OME/2016-06"

    id: str = Field(
        default="__auto_sequence__",
        pattern=r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:\S+)|(\S+)",
        json_schema_extra={
            "name": "ID",
            "type": "Attribute",
            "required": True,
            "pattern": r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:\S+)|(\S+)",
        },
    )
