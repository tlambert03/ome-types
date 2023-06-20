from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .experimenter_group_ref import ExperimenterGroupRef
from .experimenter_ref import ExperimenterRef
from .image_ref import ImageRef
from .simple_types import DatasetID


class Dataset(OMEType):
    """An element specifying a collection of images that are always processed
    together.

    Images can belong to more than one Dataset, and a Dataset may contain more
    than one Image. Images contain one or more DatasetRef elements to specify what
    datasets they belong to. Once a Dataset has been processed in any way, its
    collection of images cannot be altered. The ExperimenterRef and
    ExperimenterGroupRef elements specify the person and group this Dataset
    belongs to. Projects may contain one or more Datasets, and Datasets may belong
    to one or more Projects. This relationship is specified by listing DatasetRef
    elements within the Project element.

    Parameters
    ----------
    id : DatasetID
    annotation_ref : AnnotationRef, optional
    description : str, optional
        A description for the dataset.
    experimenter_group_ref : ExperimenterGroupRef, optional
    experimenter_ref : ExperimenterRef, optional
    image_ref : ImageRef, optional
    name : str, optional
        A name for the dataset that is suitable for presentation to the user.
    """

    id: DatasetID
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    description: Optional[str] = None
    experimenter_group_ref: Optional[ExperimenterGroupRef] = None
    experimenter_ref: Optional[ExperimenterRef] = None
    image_ref: List[ImageRef] = Field(default_factory=list)
    name: Optional[str] = None
