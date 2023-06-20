from typing import Optional

from ome_types._base_type import OMEType

from .map import Map
from .simple_types import PercentFraction, UnitsPressure, UnitsTemperature


class ImagingEnvironment(OMEType):
    """This describes the environment that the biological sample was in during the
    experiment.

    Parameters
    ----------
    air_pressure : float, optional
        AirPressure is the define units.
    air_pressure_unit : UnitsPressure, optional
        The units the AirPressure is in - default:millibars.
    co2_percent : PercentFraction, optional
        Carbon Dioxide concentration around the sample A fraction, as a value
        from 0.0 to 1.0.
    humidity : PercentFraction, optional
        Humidity around the sample A fraction, as a value from 0.0 to 1.0.
    map : Map, optional
    temperature : float, optional
        The Temperature is the define units.
    temperature_unit : UnitsTemperature, optional
        The units the Temperature is in - default:Celsius.
    """

    air_pressure: Optional[float] = None
    air_pressure_unit: Optional[UnitsPressure] = UnitsPressure("mbar")
    co2_percent: Optional[PercentFraction] = None
    humidity: Optional[PercentFraction] = None
    map: Optional[Map] = None
    temperature: Optional[float] = None
    temperature_unit: Optional[UnitsTemperature] = UnitsTemperature("°C")
