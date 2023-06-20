from datetime import datetime
from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .simple_types import PlateAcquisitionID, PositiveInt
from .well_sample_ref import WellSampleRef


class PlateAcquisition(OMEType):
    """PlateAcquisition is used to describe a single acquisition run for a plate.

    This object is used to record the set of images acquired in a single
    acquisition run. The Images for this run are linked to PlateAcquisition
    through WellSample.

    Parameters
    ----------
    id : PlateAcquisitionID
    annotation_ref : AnnotationRef, optional
    description : str, optional
        A description for the PlateAcquisition.
    end_time : datetime, optional
        Time when the last image of this acquisition was collected
    maximum_field_count : PositiveInt, optional
        The maximum number of fields (well samples) in any well in this
        PlateAcquisition. This is only used to speed up user interaction by
        stopping the reading of every well sample.
    name : str, optional
    start_time : datetime, optional
        Time when the first image of this acquisition was collected
    well_sample_ref : WellSampleRef, optional
    """

    id: PlateAcquisitionID
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    description: Optional[str] = None
    end_time: Optional[datetime] = None
    maximum_field_count: Optional[PositiveInt] = None
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    well_sample_ref: List[WellSampleRef] = Field(default_factory=list)
