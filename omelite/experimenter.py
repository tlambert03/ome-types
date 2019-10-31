from dataclasses import dataclass, field  # seems to be necessary for pyright
from typing import Optional
from uuid import UUID, uuid4

from pydantic.dataclasses import dataclass  # noqa
from pydantic.networks import EmailStr


@dataclass
class Experimenter:
    """This element describes a person who performed an imaging experiment.
    This person may also be a user of the OME system, in which case the UserName element
    contains their login name. Experimenters may belong to one or more groups which are
    specified using one or more ExperimenterGroupRef elements.
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    user_name: Optional[str] = None
    institution: Optional[str] = None
    email: Optional[EmailStr] = None
    id: UUID = field(default_factory=uuid4, init=False, repr=False)
