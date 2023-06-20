from typing_extensions import Literal

from ome_types._base_type import OMEType

from .light_source import LightSource


class LightEmittingDiode(LightSource, OMEType):
    """The LightEmittingDiode element is used to describe various kinds of LED lamps.

    As the LightEmittingDiode is inside a LightSource it already has available the
    values from ManufacturerSpec (Manufacturer, Model, SerialNumber, LotNumber)
    And the values from LightSource which includes Power in milliwatts

    We have looked at extending this element but have had a problem producing a
    generic solution.

    Possible attributes talked about adding include: Power in lumens - but this is
    complicated by multi-channel devices like CoolLED where each channel's power
    is different Wavelength Range - not a simple value so would require multiple
    attributes or a child element Angle of Projection - this would be further
    affected by the optics used for filtering the naked LED or that combine power
    from multiple devices

    These values are further affected if you over-drive the LED resulting in a
    more complex system

    Another issue is that LED's may not be used directly for illumination but as
    drivers for secondary emissions from doped fiber optics. This would require
    the fiber optics to be modeled.

    Thanks to Paul Goodwin of Applied Precision of information about this topic.

    Parameters
    ----------
    id : LightSourceID
        A LightSource ID must be specified for each light source, and the
        individual light sources can be referred to by their LightSource IDs
        (eg from Channel).
    annotation_ref : AnnotationRef, optional
    lot_number : str, optional
        The lot number of the component.
    manufacturer : str, optional
        The manufacturer of the component.
    model : str, optional
        The Model of the component.
    power : float, optional
        The light-source power. Units are set by PowerUnit.
    power_unit : UnitsPower, optional
        The units of the Power - default:milliwatts.
    serial_number : str, optional
        The serial number of the component.
    """

    kind: Literal["light_emitting_diode"] = "light_emitting_diode"
