from typing import Optional

from ome_types._base_type import OMEType

from .simple_types import NonNegativeFloat, PercentFraction, PositiveFloat, UnitsLength


class TransmittanceRange(OMEType):
    """This records the range of wavelengths that are transmitted by the filter.

    It also records the maximum amount of light transmitted.

    Parameters
    ----------
    cut_in : PositiveFloat, optional
        CutIn is the wavelength below which there is less than 50%
        transmittance for a filter. Units are set by CutInUnit.
    cut_in_tolerance : NonNegativeFloat, optional
        CutInTolerance. Units are set by CutInToleranceUnit.
    cut_in_tolerance_unit : UnitsLength, optional
        The units of the CutInTolerance - default:nanometres.
    cut_in_unit : UnitsLength, optional
        The units of the CutIn - default:nanometres.
    cut_out : PositiveFloat, optional
        CutOut is the wavelength above which there is less than 50%
        transmittance for a filter. Units are set by CutOutUnit.
    cut_out_tolerance : NonNegativeFloat, optional
        CutOutTolerance. Units are set by CutOutToleranceUnit.
    cut_out_tolerance_unit : UnitsLength, optional
        The units of the CutOutTolerance - default:nanometres.
    cut_out_unit : UnitsLength, optional
        The units of the CutOut - default:nanometres.
    transmittance : PercentFraction, optional
        The amount of light the filter transmits at a maximum A fraction, as a
        value from 0.0 to 1.0.
    """

    cut_in: Optional[PositiveFloat] = None
    cut_in_tolerance: Optional[NonNegativeFloat] = None
    cut_in_tolerance_unit: Optional[UnitsLength] = UnitsLength("nm")
    cut_in_unit: Optional[UnitsLength] = UnitsLength("nm")
    cut_out: Optional[PositiveFloat] = None
    cut_out_tolerance: Optional[NonNegativeFloat] = None
    cut_out_tolerance_unit: Optional[UnitsLength] = UnitsLength("nm")
    cut_out_unit: Optional[UnitsLength] = UnitsLength("nm")
    transmittance: Optional[PercentFraction] = None
