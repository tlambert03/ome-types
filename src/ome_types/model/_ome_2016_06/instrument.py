from typing import Any, Dict, List, Optional

from pydantic import Field, root_validator

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .detector import Detector
from .dichroic import Dichroic
from .filter import Filter
from .filter_set import FilterSet
from .light_source_group import LightSourceGroupType
from .microscope import Microscope
from .objective import Objective
from .simple_types import InstrumentID


class Instrument(OMEType):
    """This element describes the instrument used to capture the Image.

    It is primarily a container for manufacturer's model and catalog numbers for
    the Microscope, LightSource, Detector, Objective and Filters components. The
    Objective element contains the additional elements LensNA and Magnification.
    The Filters element can be composed either of separate excitation, emission
    filters and a dichroic mirror or a single filter set. Within the Image itself,
    a reference is made to this one Filter element. There may be multiple light
    sources, detectors, objectives and filters on a microscope. Each of these has
    their own ID attribute, which can be referred to from Channel. It is
    understood that the light path configuration can be different for each
    channel, but cannot be different for each timepoint or each plane of an XYZ
    stack.

    Parameters
    ----------
    id : InstrumentID
    annotation_ref : AnnotationRef, optional
    detectors : Detector, optional
    dichroics : Dichroic, optional
    filter_sets : FilterSet, optional
    filters : Filter, optional
    light_source_group : List[LightSourceGroupType], optional
    microscope : Microscope, optional
    objectives : Objective, optional
    """

    id: InstrumentID
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    detectors: List[Detector] = Field(default_factory=list)
    dichroics: List[Dichroic] = Field(default_factory=list)
    filter_sets: List[FilterSet] = Field(default_factory=list)
    filters: List[Filter] = Field(default_factory=list)
    light_source_group: List[LightSourceGroupType] = Field(default_factory=list)
    microscope: Optional[Microscope] = None
    objectives: List[Objective] = Field(default_factory=list)

    @root_validator(pre=True)
    def _root(cls, value: Dict[str, Any]):
        light_sources = {i.snake_name() for i in LightSourceGroupType.__args__}  # type: ignore
        lights = []
        for key in list(value):
            kind = {"kind": key}
            if key in light_sources:
                val = value.pop(key)
                if isinstance(val, dict):
                    lights.append({**val, **kind})
                elif isinstance(val, list):
                    lights.extend({**v, **kind} for v in val)
        if lights:
            value.setdefault("light_source_group", [])
            value["light_source_group"].extend(lights)
        return value
