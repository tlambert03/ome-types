from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .simple_types import ExperimenterID


class Experimenter(OMEType):
    """This element describes a person who performed an imaging experiment.

    This person may also be a user of the OME system, in which case the UserName
    element contains their login name. Experimenters may belong to one or more
    groups which are specified using one or more ExperimenterGroupRef elements.

    Parameters
    ----------
    id : ExperimenterID
    annotation_ref : AnnotationRef, optional
    email : str, optional
        A person's email address.
    first_name : str, optional
        First name, sometime called christian name or given name or forename.
        [plain text string]
    institution : str, optional
        A person's Institution The organizing structure that people belong to
        other than groups.  A university, or company, etc. We do not specify a
        department element, and do not mean for Institution to be used in this
        way. We simply wish to say XXX at YYY.  Where YYY has a better chance
        of being tied to a geographically fixed location and of being more
        recognizable than a group of experimenters.
    last_name : str, optional
        A person's last name sometimes called surname or family name. [plain
        text string]
    middle_name : str, optional
        Any other names.
    user_name : str, optional
        This is the username of the experimenter (in a 'unix' or 'database'
        sense).
    """

    id: ExperimenterID
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    email: Optional[str] = None
    first_name: Optional[str] = None
    institution: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    user_name: Optional[str] = None
