from typing import Any, Callable, Dict, Generator, List, Optional
from xml.etree import ElementTree

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .text_annotation import TextAnnotation


class Element(ElementTree.Element):
    """ElementTree.Element that supports pydantic validation."""

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[Any], Any], None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> ElementTree.Element:
        if isinstance(v, ElementTree.Element):
            return v
        try:
            return ElementTree.fromstring(v)
        except ElementTree.ParseError as e:
            raise ValueError(f"Invalid XML string: {e}")


class XMLAnnotation(TextAnnotation, OMEType):
    """An general xml annotation.

    The contents of this is not processed as OME XML but should still be well-
    formed XML.

    Parameters
    ----------
    id : AnnotationID
    value : Element
    annotation_ref : AnnotationRef, optional
    annotator : ExperimenterID, optional
        The Annotator is the person who attached this annotation. e.g. If
        UserA annotates something with TagB, owned by UserB, UserA is still
        the Annotator.
    description : str, optional
        A description for the annotation.
    namespace : str, optional
        We recommend the inclusion of a namespace for annotations you define.
        If it is absent then we assume the annotation is to use our (OME's)
        default interpretation for this type.
    """

    value: Element
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    description: Optional[str] = None

    # NOTE: pickling this object requires xmlschema>=1.4.1

    def dict(self, **k: Any) -> Dict[str, Any]:
        d = super().dict(**k)
        d["value"] = ElementTree.tostring(
            d.pop("value"), encoding="unicode", method="xml"
        ).strip()
        return d
