from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .simple_types import ReagentID


class Reagent(OMEType):
    """Reagent is used to describe a chemical or some other physical experimental
    parameter.

    Parameters
    ----------
    id : ReagentID
    annotation_ref : AnnotationRef, optional
    description : str, optional
        A long description for the reagent.
    name : str, optional
        A short name for the reagent
    reagent_identifier : str, optional
        This is a reference to an external (to OME) representation of the
        Reagent. It serves as a foreign key into an external database. - It is
        sometimes referred to as ExternalIdentifier.
    """

    id: ReagentID
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    description: Optional[str] = None
    name: Optional[str] = None
    reagent_identifier: Optional[str] = None
