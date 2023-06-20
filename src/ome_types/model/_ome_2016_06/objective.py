from enum import Enum
from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .manufacturer_spec import ManufacturerSpec
from .simple_types import ObjectiveID, UnitsLength


class Correction(Enum):
    """The correction applied to the lens."""

    ACHRO = "Achro"
    ACHROMAT = "Achromat"
    APO = "Apo"
    FL = "Fl"
    FLUAR = "Fluar"
    FLUOR = "Fluor"
    FLUOTAR = "Fluotar"
    NEOFLUAR = "Neofluar"
    OTHER = "Other"
    PLAN_APO = "PlanApo"
    PLAN_FLUOR = "PlanFluor"
    PLAN_NEOFLUAR = "PlanNeofluar"
    SUPER_FLUOR = "SuperFluor"
    UV = "UV"
    VIOLET_CORRECTED = "VioletCorrected"


class Immersion(Enum):
    """The immersion medium the lens is designed for."""

    AIR = "Air"
    GLYCEROL = "Glycerol"
    MULTI = "Multi"
    OIL = "Oil"
    OTHER = "Other"
    WATER = "Water"
    WATER_DIPPING = "WaterDipping"


class Objective(ManufacturerSpec, OMEType):
    """A description of the microscope's objective lens.

    Required elements include the lens numerical aperture, and the magnification,
    both of which a floating point (real) numbers. The values are those that are
    fixed for a particular objective: either because it has been manufactured to
    this specification or the value has been measured on this particular
    objective. Correction: This is the type of correction coating applied to this
    lens. Immersion: This is the types of immersion medium the lens is designed to
    work with. It is not the same as 'Medium' in ObjectiveRef (a single type) as
    here Immersion can have compound values like 'Multi'. LensNA: The numerical
    aperture of the lens (as a float) NominalMagnification: The specified
    magnification e.g. x10 CalibratedMagnification: The measured magnification
    e.g. x10.3 WorkingDistance: WorkingDistance of the lens.

    Parameters
    ----------
    id : ObjectiveID
    annotation_ref : AnnotationRef, optional
    calibrated_magnification : float, optional
        The magnification of the lens as measured by a calibration process-
        i.e. '59.987' for a 60X lens.
    correction : Correction, optional
        The correction applied to the lens
    immersion : Immersion, optional
        The immersion medium the lens is designed for
    iris : bool, optional
        Records whether or not the objective was fitted with an Iris.
    lens_na : float, optional
        The numerical aperture of the lens expressed as a floating point
        (real) number. Expected range 0.02 - 1.5
    lot_number : str, optional
        The lot number of the component.
    manufacturer : str, optional
        The manufacturer of the component.
    model : str, optional
        The Model of the component.
    nominal_magnification : float, optional
        The magnification of the lens as specified by the manufacturer - i.e.
        '60' is a 60X lens. Note: The type of this has been changed from int
        to float to allow the specification of additional lenses e.g. 0.5X
        lens
    serial_number : str, optional
        The serial number of the component.
    working_distance : float, optional
        The working distance of the lens expressed as a floating point (real)
        number. Units are set by WorkingDistanceUnit.
    working_distance_unit : UnitsLength, optional
        The units of the working distance - default:microns.
    """

    id: ObjectiveID
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    calibrated_magnification: Optional[float] = None
    correction: Optional[Correction] = None
    immersion: Optional[Immersion] = None
    iris: Optional[bool] = None
    lens_na: Optional[float] = None
    nominal_magnification: Optional[float] = None
    working_distance: Optional[float] = None
    working_distance_unit: Optional[UnitsLength] = UnitsLength("µm")
