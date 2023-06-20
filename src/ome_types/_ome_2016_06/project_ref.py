from ome_types._base_type import OMEType

from .reference import Reference
from .simple_types import ProjectID


class ProjectRef(Reference, OMEType):
    """There may be one or more of these in a Dataset.

    This empty element has a required Project ID attribute that refers to Projects
    defined within the OME element.

    Parameters
    ----------
    id : ProjectID
    """

    id: ProjectID
