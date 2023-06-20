from datetime import datetime
from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .experiment_ref import ExperimentRef
from .experimenter_group_ref import ExperimenterGroupRef
from .experimenter_ref import ExperimenterRef
from .imaging_environment import ImagingEnvironment
from .instrument_ref import InstrumentRef
from .microbeam_manipulation_ref import MicrobeamManipulationRef
from .objective_settings import ObjectiveSettings
from .pixels import Pixels
from .roi_ref import ROIRef
from .simple_types import ImageID
from .stage_label import StageLabel


class Image(OMEType):
    """This element describes the actual image and its meta-data.

    The elements that are references (ending in Ref or Settings) refer to elements
    defined outside of the Image element. Ref elements are simple links, while
    Settings elements are links with additional values.

    If any of the required Image attributes or elements are missing, its
    guaranteed to be an invalid document. The required attributes and elements are
    ID and Pixels.

    ExperimenterRef is required for all Images with well formed LSIDs. ImageType
    is a vendor-specific designation of the type of image this is. Examples of
    ImageType include 'STK', 'SoftWorx', etc. The Name attributes are in all cases
    the name of the element instance. In this case, the name of the image, not
    necessarily the filename. Physical size of pixels are microns[µm].

    Parameters
    ----------
    id : ImageID
    pixels : Pixels
    acquisition_date : datetime, optional
        The acquisition date of the Image. The element contains an
        xsd:dateTime string based on the ISO 8601 format (i.e.
        1988-04-07T18:39:09.359)  YYYY-MM-DDTHH:mm:SS.sssZ Y - Year M - Month
        D - Day H - Hour m - minutes S - Seconds s - sub-seconds (optional) Z
        - Zone (optional) +HH:mm or -HH:mm or Z for UTC  Note: xsd:dataTime
        supports a very wide date range with unlimited precision. The full
        date range and precision are not typically supported by platform- and
        language-specific libraries. Where the supported time precision is
        less than the precision used by the xsd:dateTime timestamp there will
        be loss of precision; this will typically occur via direct truncation
        or (less commonly) rounding.  The year value can be large and/or
        negative. Any value covering the current or last century should be
        correctly processed, but some systems cannot process earlier dates.
        The sub-second value is defined as an unlimited number of digits after
        the decimal point. In Java a minimum of millisecond precision is
        guaranteed. In C++ microsecond precision is guaranteed, with
        nanosecond precision being available on some platforms.  Time zones
        are supported, eg '2013-10-24T11:52:33+01:00' for Paris, but in most
        cases it will be converted to UTC when the timestamp is written.
    annotation_ref : AnnotationRef, optional
    description : str, optional
        A description for the image.
    experiment_ref : ExperimentRef, optional
    experimenter_group_ref : ExperimenterGroupRef, optional
    experimenter_ref : ExperimenterRef, optional
    imaging_environment : ImagingEnvironment, optional
    instrument_ref : InstrumentRef, optional
    microbeam_manipulation_ref : MicrobeamManipulationRef, optional
    name : str, optional
    objective_settings : ObjectiveSettings, optional
    roi_ref : ROIRef, optional
    stage_label : StageLabel, optional
    """

    id: ImageID
    pixels: Pixels
    acquisition_date: Optional[datetime] = None
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    description: Optional[str] = None
    experiment_ref: Optional[ExperimentRef] = None
    experimenter_group_ref: Optional[ExperimenterGroupRef] = None
    experimenter_ref: Optional[ExperimenterRef] = None
    imaging_environment: Optional[ImagingEnvironment] = None
    instrument_ref: Optional[InstrumentRef] = None
    microbeam_manipulation_ref: List[MicrobeamManipulationRef] = Field(
        default_factory=list
    )
    name: Optional[str] = None
    objective_settings: Optional[ObjectiveSettings] = None
    roi_ref: List[ROIRef] = Field(default_factory=list)
    stage_label: Optional[StageLabel] = None
