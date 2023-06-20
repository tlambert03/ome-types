from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .experimenter_ref import ExperimenterRef
from .leader import Leader
from .simple_types import ExperimenterGroupID


class ExperimenterGroup(OMEType):
    """The ExperimenterGroupID is required.

    Information should ideally be specified for at least one Leader as a contact
    for the group. The Leaders are themselves Experimenters.

    Parameters
    ----------
    id : ExperimenterGroupID
    annotation_ref : AnnotationRef, optional
    description : str, optional
        A description for the group.
    experimenter_ref : ExperimenterRef, optional
    leader : Leader, optional
    name : str, optional
    """

    id: ExperimenterGroupID
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    description: Optional[str] = None
    experimenter_ref: List[ExperimenterRef] = Field(default_factory=list)
    leader: List[Leader] = Field(default_factory=list)
    name: Optional[str] = None
