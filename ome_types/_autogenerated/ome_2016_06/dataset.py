from typing import Optional

from pydantic import Field

from ome_types._autogenerated.ome_2016_06.annotation_ref import AnnotationRef
from ome_types._autogenerated.ome_2016_06.experimenter_group_ref import (
    ExperimenterGroupRef,
)
from ome_types._autogenerated.ome_2016_06.experimenter_ref import (
    ExperimenterRef,
)
from ome_types._autogenerated.ome_2016_06.image_ref import ImageRef
from ome_types._mixins._base_type import OMEType

__NAMESPACE__ = "http://www.openmicroscopy.org/Schemas/OME/2016-06"


class Dataset(OMEType):
    """An element specifying a collection of images that are always processed
    together.

    Images can belong to more than one Dataset, and a Dataset may
    contain more than one Image. Images contain one or more DatasetRef
    elements to specify what datasets they belong to. Once a Dataset has
    been processed in any way, its collection of images cannot be
    altered. The ExperimenterRef and ExperimenterGroupRef elements
    specify the person and group this Dataset belongs to. Projects may
    contain one or more Datasets, and Datasets may belong to one or more
    Projects. This relationship is specified by listing DatasetRef
    elements within the Project element.

    Attributes
    ----------
    description : None | str
        A description for the dataset. [plain-text multi-line string]
    experimenter_ref : None | ExperimenterRef
        (The Dataset ExperimenterRef).
    experimenter_group_ref : None | ExperimenterGroupRef
        (The Dataset ExperimenterGroupRef).
    image_refs : list[ImageRef]
        (The Dataset ImageRefs).
    annotation_refs : list[AnnotationRef]
        (The Dataset AnnotationRefs).
    name : None | str
        A name for the dataset that is suitable for presentation to the user.
    id : str
        (The Dataset ID).
    """

    class Meta:
        namespace = "http://www.openmicroscopy.org/Schemas/OME/2016-06"

    description: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "name": "Description",
            "type": "Element",
            "white_space": "preserve",
        },
    )
    experimenter_ref: Optional[ExperimenterRef] = Field(
        default=None,
        json_schema_extra={
            "name": "ExperimenterRef",
            "type": "Element",
        },
    )
    experimenter_group_ref: Optional[ExperimenterGroupRef] = Field(
        default=None,
        json_schema_extra={
            "name": "ExperimenterGroupRef",
            "type": "Element",
        },
    )
    image_refs: list[ImageRef] = Field(
        default_factory=list,
        json_schema_extra={
            "name": "ImageRef",
            "type": "Element",
        },
    )
    annotation_refs: list[AnnotationRef] = Field(
        default_factory=list,
        json_schema_extra={
            "name": "AnnotationRef",
            "type": "Element",
        },
    )
    name: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "name": "Name",
            "type": "Attribute",
        },
    )
    id: str = Field(
        default="__auto_sequence__",
        pattern=r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Dataset:\S+)|(Dataset:\S+)",
        json_schema_extra={
            "name": "ID",
            "type": "Attribute",
            "required": True,
            "pattern": r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Dataset:\S+)|(Dataset:\S+)",
        },
    )