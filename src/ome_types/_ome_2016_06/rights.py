from typing import Optional

from ome_types._base_type import OMEType


class Rights(OMEType):
    """The rights holder of this data and the rights held.

    Parameters
    ----------
    rights_held : str, optional
        The rights held by the rights holder. e.g. "All rights reserved" or
        "Creative Commons Attribution 3.0 Unported License"
    rights_holder : str, optional
        The rights holder for this data. e.g. "Copyright (C) 2002 - 2016 Open
        Microscopy Environment"
    """

    rights_held: Optional[str] = None
    rights_holder: Optional[str] = None
