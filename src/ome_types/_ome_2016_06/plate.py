from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .plate_acquisition import PlateAcquisition
from .simple_types import (
    NamingConvention,
    NonNegativeInt,
    PlateID,
    PositiveInt,
    UnitsLength,
)
from .well import Well


class Plate(OMEType):
    """This element identifies microtiter plates within a screen.

    A plate can belong to more than one screen. The Screen(s) that a plate belongs
    to are specified by the ScreenRef element. The Plate ID and Name attributes
    are required. The Wells in a plate are numbers from the top-left corner in a
    grid starting at zero. i.e. The top-left well of a plate is index (0,0)

    Parameters
    ----------
    id : PlateID
    annotation_ref : AnnotationRef, optional
    column_naming_convention : NamingConvention, optional
        The ColumnNamingConvention
    columns : PositiveInt, optional
        The number of columns in the plate
    description : str, optional
        A description for the plate.
    external_identifier : str, optional
        The ExternalIdentifier attribute may contain a reference to an
        external database.
    field_index : NonNegativeInt, optional
        The index of the WellSample to display as the default Field
    name : str, optional
        The Name identifies the plate to the user. It is used much like the
        ID, and so must be unique within the document.  If a plate name is not
        available when one is needed it will be constructed in the following
        order: 1. If name is available use it. 2. If not use "Start time - End
        time" (NOTE: Not a subtraction! A string representation of the two
        times separated by a dash.) 3. If these times are not available use
        the Plate ID.
    plate_acquisitions : PlateAcquisition, optional
    row_naming_convention : NamingConvention, optional
        The RowNamingConvention
    rows : PositiveInt, optional
        The number of rows in the plate
    status : str, optional
        A textual annotation of the current state of the plate with respect to
        the experiment work-flow; e.g. 1. Seed cell: done; 2. Transfection:
        done;      3. Gel doc: todo.
    well_origin_x : float, optional
        This defines the X position to use for the origin of the fields
        (individual images) taken in a well. It is used with the X in the
        WellSample to display the fields in the correct position relative to
        each other. Each Well in the plate has the same well origin. Units are
        set by WellOriginXUnit.  In the OMERO clients by convention we display
        the WellOrigin in the center of the view.
    well_origin_x_unit : UnitsLength, optional
        The units of the well origin in X - default:reference frame.
    well_origin_y : float, optional
        This defines the Y position to use for the origin of the fields
        (individual images) taken in a well. It is used with the Y in the
        WellSample to display the fields in the correct position relative to
        each other. Each Well in the plate has the same well origin.  Units
        are set by WellOriginYUnit.  In the OMERO clients by convention we
        display the WellOrigin in the center of the view.
    well_origin_y_unit : UnitsLength, optional
        The units of the well origin in Y - default:reference frame.
    wells : Well, optional
    """

    id: PlateID
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    column_naming_convention: Optional[NamingConvention] = None
    columns: Optional[PositiveInt] = None
    description: Optional[str] = None
    external_identifier: Optional[str] = None
    field_index: Optional[NonNegativeInt] = None
    name: Optional[str] = None
    plate_acquisitions: List[PlateAcquisition] = Field(default_factory=list)
    row_naming_convention: Optional[NamingConvention] = None
    rows: Optional[PositiveInt] = None
    status: Optional[str] = None
    well_origin_x: Optional[float] = None
    well_origin_x_unit: Optional[UnitsLength] = UnitsLength("reference frame")
    well_origin_y: Optional[float] = None
    well_origin_y_unit: Optional[UnitsLength] = UnitsLength("reference frame")
    wells: List[Well] = Field(default_factory=list)
