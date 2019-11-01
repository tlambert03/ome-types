from dataclasses import dataclass, field  # seems to be necessary for pyright
from .image import Image
from .experimenter import Experimenter
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic.dataclasses import dataclass  # noqa


@dataclass
class Dataset:
    """A collection of images that are always processed together.

    Images can belong to more than one Dataset, and a Dataset may contain more than one
    Image. Once a Dataset has been processed in any way, its collection of images cannot
    be altered. The ExperimenterRef and ExperimenterGroupRef elements specify the person and
    group this Dataset belongs to. Projects may contain one or more Datasets, and Datasets
    may belong to one or more Projects. This relationship is specified by listing DatasetRef
    elements within the Project element.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    experimenter: Optional[Experimenter] = None
    images: List[Image] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4, init=False, repr=False)

    # # UNUSED
    # experimenter_group: Optional[ExperimenterGroup] = None
    # annotations: List[Annotation] = field(default_factory=list)
