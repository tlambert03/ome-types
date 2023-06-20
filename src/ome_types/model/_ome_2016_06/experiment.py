from enum import Enum
from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .experimenter_ref import ExperimenterRef
from .microbeam_manipulation import MicrobeamManipulation
from .simple_types import ExperimentID


class Type(Enum):
    """A term to describe the type of experiment."""

    COLOCALIZATION = "Colocalization"
    ELECTROPHYSIOLOGY = "Electrophysiology"
    FISH = "FISH"
    FLUORESCENCE_LIFETIME = "FluorescenceLifetime"
    FOUR_D_PLUS = "FourDPlus"
    FP = "FP"
    FRET = "FRET"
    IMMUNOCYTOCHEMISTRY = "Immunocytochemistry"
    IMMUNOFLUORESCENCE = "Immunofluorescence"
    ION_IMAGING = "IonImaging"
    OTHER = "Other"
    PGI_DOCUMENTATION = "PGIDocumentation"
    PHOTOBLEACHING = "Photobleaching"
    SCREEN = "Screen"
    SPECTRAL_IMAGING = "SpectralImaging"
    SPIM = "SPIM"
    TIME_LAPSE = "TimeLapse"


class Experiment(OMEType):
    """This element describes the type of experiment.

    The required Type attribute must contain one or more entries from the
    following list: FP FRET Time-lapse 4-D+ Screen Immunocytochemistry FISH
    Electrophysiology  Ion-Imaging Colocalization PGI/Documentation FRAP
    Photoablation Optical-Trapping Photoactivation Fluorescence-Lifetime Spectral-
    Imaging Other FP refers to fluorescent proteins, PGI/Documentation is not a
    'data' image. The optional Description element may contain free text to
    further describe the experiment.

    Parameters
    ----------
    id : ExperimentID
    description : str, optional
        A description for the experiment.
    experimenter_ref : ExperimenterRef, optional
        This is a link to the Experimenter who conducted the experiment
    microbeam_manipulations : MicrobeamManipulation, optional
    type : Type, optional
        A term to describe the type of experiment.
    """

    id: ExperimentID
    description: Optional[str] = None
    experimenter_ref: Optional[ExperimenterRef] = None
    microbeam_manipulations: List[MicrobeamManipulation] = Field(default_factory=list)
    type: List[Type] = Field(default_factory=list)
