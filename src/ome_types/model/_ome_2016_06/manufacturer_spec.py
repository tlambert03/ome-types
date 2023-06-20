from typing import Optional

from ome_types._base_type import OMEType


class ManufacturerSpec(OMEType):
    """This is the base from which many microscope components are extended.

    E.g Objective, Filter etc. Provides attributes for recording common properties
    of these components such as Manufacturer name, Model etc, all of which are
    optional.

    Parameters
    ----------
    lot_number : str, optional
        The lot number of the component.
    manufacturer : str, optional
        The manufacturer of the component.
    model : str, optional
        The Model of the component.
    serial_number : str, optional
        The serial number of the component.
    """

    lot_number: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
