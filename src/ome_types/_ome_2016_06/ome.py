import weakref
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, validator

from ome_types import util
from ome_types._base_type import OMEType

from .annotation import Annotation
from .boolean_annotation import BooleanAnnotation
from .comment_annotation import CommentAnnotation
from .dataset import Dataset
from .double_annotation import DoubleAnnotation
from .experiment import Experiment
from .experimenter import Experimenter
from .experimenter_group import ExperimenterGroup
from .file_annotation import FileAnnotation
from .folder import Folder
from .image import Image
from .instrument import Instrument
from .list_annotation import ListAnnotation
from .long_annotation import LongAnnotation
from .map_annotation import MapAnnotation
from .plate import Plate
from .project import Project
from .rights import Rights
from .roi import ROI
from .screen import Screen
from .simple_types import UniversallyUniqueIdentifier
from .tag_annotation import TagAnnotation
from .term_annotation import TermAnnotation
from .timestamp_annotation import TimestampAnnotation
from .xml_annotation import XMLAnnotation

_annotation_types: Dict[str, type] = {
    "boolean_annotation": BooleanAnnotation,
    "comment_annotation": CommentAnnotation,
    "double_annotation": DoubleAnnotation,
    "file_annotation": FileAnnotation,
    "list_annotation": ListAnnotation,
    "long_annotation": LongAnnotation,
    "map_annotation": MapAnnotation,
    "tag_annotation": TagAnnotation,
    "term_annotation": TermAnnotation,
    "timestamp_annotation": TimestampAnnotation,
    "xml_annotation": XMLAnnotation,
}


class BinaryOnly(OMEType):
    """Pointer to an external metadata file.

    If this              element is present, then no other metadata may be present
    in this              file, i.e. this file is a place-holder.

    Parameters
    ----------
    metadata_file : str
        Filename of the OME-XML metadata file for                  this binary
        data. If the file cannot be found, a search can                  be
        performed based on the UUID.
    uuid : UniversallyUniqueIdentifier
        The unique identifier of another OME-XML                  block whose
        metadata describes the binary data in this file.                  This
        UUID is considered authoritative regardless of
        mismatches in the filename.
    """

    metadata_file: str
    uuid: UniversallyUniqueIdentifier


class OME(OMEType):
    """The OME element is a container for all information objects accessible by OME.

    These information objects include descriptions of the imaging experiments and
    the people who perform them, descriptions of the microscope, the resulting
    images and how they were acquired, the analyses performed on those images, and
    the analysis results themselves. An OME file may contain any or all of this
    information.

    With the creation of the Metadata Only Companion OME-XML and Binary Only OME-
    TIFF files the top level OME node has changed slightly. It can EITHER: Contain
    all the previously expected elements OR: Contain a single BinaryOnly element
    that points at its Metadata Only Companion OME-XML file.

    Parameters
    ----------
    binary_only : BinaryOnly, optional
        Pointer to an external metadata file. If this              element is
        present, then no other metadata may be present in this
        file, i.e. this file is a place-holder.
    creator : str, optional
        This is the name of the creating application of the OME-XML and
        preferably its full version. e.g "CompanyName, SoftwareName,
        V2.6.3456" This is optional but we hope it will be set by applications
        writing out OME-XML from scratch.
    datasets : Dataset, optional
    experimenter_groups : ExperimenterGroup, optional
    experimenters : Experimenter, optional
    experiments : Experiment, optional
    folders : Folder, optional
    images : Image, optional
    instruments : Instrument, optional
    plates : Plate, optional
    projects : Project, optional
    rights : Rights, optional
    rois : ROI, optional
    screens : Screen, optional
    structured_annotations : List[Annotation], optional
    uuid : UniversallyUniqueIdentifier, optional
        This unique identifier is used to keep track of multi part files. It
        allows the links between files to survive renaming.  While OPTIONAL in
        the general case this is REQUIRED in a MetadataOnly Companion to a
        collection of BinaryOnly files.
    """

    binary_only: Optional[BinaryOnly] = None
    creator: Optional[str] = None
    datasets: List[Dataset] = Field(default_factory=list)
    experimenter_groups: List[ExperimenterGroup] = Field(default_factory=list)
    experimenters: List[Experimenter] = Field(default_factory=list)
    experiments: List[Experiment] = Field(default_factory=list)
    folders: List[Folder] = Field(default_factory=list)
    images: List[Image] = Field(default_factory=list)
    instruments: List[Instrument] = Field(default_factory=list)
    plates: List[Plate] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    rights: Optional[Rights] = None
    rois: List[ROI] = Field(default_factory=list)
    screens: List[Screen] = Field(default_factory=list)
    structured_annotations: List[Annotation] = Field(default_factory=list)
    uuid: Optional[UniversallyUniqueIdentifier] = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._link_refs()

    def _link_refs(self) -> None:
        ids = util.collect_ids(self)
        for ref in util.collect_references(self):
            ref._ref = weakref.ref(ids[ref.id])

    def __setstate__(self: Any, state: Dict[str, Any]) -> None:
        """Support unpickle of our weakref references."""
        super().__setstate__(state)
        self._link_refs()

    @classmethod
    def from_xml(cls, xml: Union[Path, str]) -> "OME":
        from ome_types import from_xml

        return from_xml(xml)

    @classmethod
    def from_tiff(cls, path: Union[Path, str]) -> "OME":
        from ome_types import from_tiff

        return from_tiff(path)

    def to_xml(self) -> str:
        from ome_types import to_xml

        return to_xml(self)

    @validator("structured_annotations", pre=True, each_item=True)
    def validate_structured_annotations(
        cls, value: Union[Annotation, Dict[Any, Any]]
    ) -> Annotation:
        if isinstance(value, Annotation):
            return value
        elif isinstance(value, dict):
            try:
                _type = value.pop("_type")
            except KeyError:
                raise ValueError("dict initialization requires _type") from None
            try:
                annotation_cls = _annotation_types[_type]
            except KeyError:
                raise ValueError(f"unknown Annotation type '{_type}'") from None
            return annotation_cls(**value)
        else:
            raise ValueError("invalid type for annotation values")
