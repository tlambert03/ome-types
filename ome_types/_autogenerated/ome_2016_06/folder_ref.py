from pydantic import Field

from ome_types._autogenerated.ome_2016_06.reference import Reference

__NAMESPACE__ = "http://www.openmicroscopy.org/Schemas/OME/2016-06"


class FolderRef(Reference):
    """The FolderRef element refers to a Folder by specifying the Folder ID
    attribute.

    One or more FolderRef elements may be listed within the Folder
    element to specify what Folders the Folder contains. This tree
    hierarchy must be acyclic.
    """

    class Meta:
        namespace = "http://www.openmicroscopy.org/Schemas/OME/2016-06"

    id: str = Field(
        default="__auto_sequence__",
        pattern=r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Folder:\S+)|(Folder:\S+)",
        json_schema_extra={
            "name": "ID",
            "type": "Attribute",
            "required": True,
            "pattern": r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Folder:\S+)|(Folder:\S+)",
        },
    )
