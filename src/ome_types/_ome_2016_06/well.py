from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .reagent_ref import ReagentRef
from .simple_types import Color, NonNegativeInt, WellID
from .well_sample import WellSample


class Well(OMEType):
    """A Well is a component of the Well/Plate/Screen construct to describe screening
    applications.

    A Well has a number of WellSample elements that link to the Images collected
    in this well. The ReagentRef links any Reagents that were used in this Well. A
    well is part of only one Plate. The origin for the row and column identifiers
    is the top left corner of the plate starting at zero. i.e The top left well of
    a plate is index (0,0)

    Parameters
    ----------
    column : NonNegativeInt
        This is the column index of the well, the origin is the top left
        corner of the plate with the first column of cells being column zero.
        i.e top left is (0,0) The combination of Row, Column has to be unique
        for each well in a plate.
    id : WellID
    row : NonNegativeInt
        This is the row index of the well, the origin is the top left corner
        of the plate with the first row of wells being row zero. i.e top left
        is (0,0) The combination of Row, Column has to be unique for each well
        in a plate.
    annotation_ref : AnnotationRef, optional
    color : Color, optional
        A marker color used to highlight the well - encoded as RGBA The
        default value "-1" is #FFFFFFFF so solid white (it is a signed 32 bit
        value) NOTE: Prior to the 2012-06 schema the default value was
        incorrect and produced a transparent red not solid white.
    external_description : str, optional
        A description of the externally defined identifier for this plate.
    external_identifier : str, optional
        The ExternalIdentifier attribute may contain a reference to an
        external database.
    reagent_ref : ReagentRef, optional
    type : str, optional
        A human readable identifier for the screening status. e.g. empty,
        positive control, negative control, control, experimental, etc.
    well_samples : WellSample, optional
    """

    column: NonNegativeInt
    id: WellID
    row: NonNegativeInt
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    color: Optional[Color] = Color("white")
    external_description: Optional[str] = None
    external_identifier: Optional[str] = None
    reagent_ref: Optional[ReagentRef] = None
    type: Optional[str] = None
    well_samples: List[WellSample] = Field(default_factory=list)
