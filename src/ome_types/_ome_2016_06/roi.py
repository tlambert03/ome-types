from typing import Any, Dict, Iterator, List, Optional, Sequence

from pydantic import Field, validator

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .shape_group import ShapeGroupType
from .simple_types import ROIID


class ROI(OMEType):
    """A four dimensional 'Region of Interest'.

    If they are not used, and the Image has more than one plane, the entire set of
    planes is assumed to be included in the ROI. Multiple ROIs may be specified.

    Parameters
    ----------
    id : ROIID
    annotation_ref : AnnotationRef, optional
    description : str, optional
        A description for the ROI.
    name : str, optional
        The Name identifies the ROI to the user.
    union : List[ShapeGroupType], optional
    """

    id: ROIID
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    description: Optional[str] = None
    name: Optional[str] = None
    union: List[ShapeGroupType] = Field(default_factory=list)

    @validator("union", pre=True)
    def _validate_union(cls, value: Any) -> Sequence[Dict[str, Any]]:
        if isinstance(value, dict):
            return list(cls._flatten_union_dict(value))
        if not isinstance(value, Sequence):
            raise TypeError("must be dict or sequence of dicts")
        return value

    @classmethod
    def _flatten_union_dict(
        cls, nested: Dict[str, Any], keyname: str = "kind"
    ) -> Iterator[Dict[str, Any]]:
        for key, value in nested.items():
            keydict = {keyname: key} if keyname else {}
            if isinstance(value, list):
                yield from ({**x, **keydict} for x in value)
            else:
                yield {**value, **keydict}
