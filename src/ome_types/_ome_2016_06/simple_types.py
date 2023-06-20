import re
from enum import Enum

from pydantic import color
from pydantic.types import ConstrainedFloat, ConstrainedInt, ConstrainedStr


class base64Binary(ConstrainedStr):
    pass


class Binning(Enum):
    """Represents the number of pixels that are combined to form larger pixels.

    {used:CCD,EMCCD}.
    """

    EIGHTBYEIGHT = "8x8"
    FOURBYFOUR = "4x4"
    ONEBYONE = "1x1"
    OTHER = "Other"
    TWOBYTWO = "2x2"


class Color(color.Color):
    def __init__(self, val: color.ColorType) -> None:
        if isinstance(val, int):
            val = self._int2tuple(val)
        super().__init__(val)

    @classmethod
    def _int2tuple(cls, val: int):
        return (val >> 24 & 255, val >> 16 & 255, val >> 8 & 255, (val & 255) / 255)

    def as_int32(self) -> int:
        r, g, b, *a = self.as_rgb_tuple()
        v = r << 24 | g << 16 | b << 8 | int((a[0] if a else 1) * 255)
        if v < 2**32 // 2:
            return v
        return v - 2**32

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Color):
            return self.as_int32() == o.as_int32()
        return False

    def __int__(self) -> int:
        return self.as_int32()


class FontFamily(Enum):
    """The font family used to draw the text.

    [enumeration] Note: these values are all lower case so they match the standard
    HTML/CSS values. "fantasy" has been included for completeness we do not
    recommended its regular use.
    """

    CURSIVE = "cursive"
    FANTASY = "fantasy"
    MONOSPACE = "monospace"
    SANSSERIF = "sans-serif"
    SERIF = "serif"


class Hex40(ConstrainedStr):
    min_length = 40
    max_length = 40


class LSID(ConstrainedStr):
    regex = re.compile(r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:\S+:\S+)|(\S+:\S+)")


class Marker(Enum):
    """Shape of marker on the end of a line.

    [enumeration].
    """

    ARROW = "Arrow"


class NamingConvention(Enum):
    """Predefined list of values for the well labels."""

    LETTER = "letter"
    NUMBER = "number"


class NonNegativeFloat(ConstrainedFloat):
    ge = 0.0


class NonNegativeInt(ConstrainedInt):
    ge = 0


class NonNegativeLong(ConstrainedInt):
    ge = 0


class PercentFraction(ConstrainedFloat):
    le = 1.0
    ge = 0.0


class PixelType(Enum):
    """The number size/kind used to represent a pixel."""

    BIT = "bit"
    COMPLEXDOUBLE = "double-complex"
    COMPLEXFLOAT = "complex"
    DOUBLE = "double"
    FLOAT = "float"
    INT16 = "int16"
    INT32 = "int32"
    INT8 = "int8"
    UINT16 = "uint16"
    UINT32 = "uint32"
    UINT8 = "uint8"


class PositiveFloat(ConstrainedFloat):
    gt = 0.0


class PositiveInt(ConstrainedInt):
    ge = 1


class UnitsAngle(Enum):
    """The units used to represent an angle."""

    DEGREE = "deg"
    GRADIAN = "gon"
    RADIAN = "rad"


class UnitsElectricPotential(Enum):
    """The units used to represent an electric potential."""

    ATTOVOLT = "aV"
    CENTIVOLT = "cV"
    DECAVOLT = "daV"
    DECIVOLT = "dV"
    EXAVOLT = "EV"
    FEMTOVOLT = "fV"
    GIGAVOLT = "GV"
    HECTOVOLT = "hV"
    KILOVOLT = "kV"
    MEGAVOLT = "MV"
    MICROVOLT = "µV"
    MILLIVOLT = "mV"
    NANOVOLT = "nV"
    PETAVOLT = "PV"
    PICOVOLT = "pV"
    TERAVOLT = "TV"
    VOLT = "V"
    YOCTOVOLT = "yV"
    YOTTAVOLT = "YV"
    ZEPTOVOLT = "zV"
    ZETTAVOLT = "ZV"


class UnitsFrequency(Enum):
    """The units used to represent frequency."""

    ATTOHERTZ = "aHz"
    CENTIHERTZ = "cHz"
    DECAHERTZ = "daHz"
    DECIHERTZ = "dHz"
    EXAHERTZ = "EHz"
    FEMTOHERTZ = "fHz"
    GIGAHERTZ = "GHz"
    HECTOHERTZ = "hHz"
    HERTZ = "Hz"
    KILOHERTZ = "kHz"
    MEGAHERTZ = "MHz"
    MICROHERTZ = "µHz"
    MILLIHERTZ = "mHz"
    NANOHERTZ = "nHz"
    PETAHERTZ = "PHz"
    PICOHERTZ = "pHz"
    TERAHERTZ = "THz"
    YOCTOHERTZ = "yHz"
    YOTTAHERTZ = "YHz"
    ZEPTOHERTZ = "zHz"
    ZETTAHERTZ = "ZHz"


class UnitsLength(Enum):
    """The units used to represent a length."""

    ANGSTROM = "Å"
    ASTRONOMICALUNIT = "ua"
    ATTOMETER = "am"
    CENTIMETER = "cm"
    DECAMETER = "dam"
    DECIMETER = "dm"
    EXAMETER = "Em"
    FEMTOMETER = "fm"
    FOOT = "ft"
    GIGAMETER = "Gm"
    HECTOMETER = "hm"
    INCH = "in"
    KILOMETER = "km"
    LIGHTYEAR = "ly"
    LINE = "li"
    MEGAMETER = "Mm"
    METER = "m"
    MICROMETER = "µm"
    MILE = "mi"
    MILLIMETER = "mm"
    NANOMETER = "nm"
    PARSEC = "pc"
    PETAMETER = "Pm"
    PICOMETER = "pm"
    PIXEL = "pixel"
    POINT = "pt"
    REFERENCEFRAME = "reference frame"
    TERAMETER = "Tm"
    THOU = "thou"
    YARD = "yd"
    YOCTOMETER = "ym"
    YOTTAMETER = "Ym"
    ZEPTOMETER = "zm"
    ZETTAMETER = "Zm"


class UnitsPower(Enum):
    """The units used to represent power."""

    ATTOWATT = "aW"
    CENTIWATT = "cW"
    DECAWATT = "daW"
    DECIWATT = "dW"
    EXAWATT = "EW"
    FEMTOWATT = "fW"
    GIGAWATT = "GW"
    HECTOWATT = "hW"
    KILOWATT = "kW"
    MEGAWATT = "MW"
    MICROWATT = "µW"
    MILLIWATT = "mW"
    NANOWATT = "nW"
    PETAWATT = "PW"
    PICOWATT = "pW"
    TERAWATT = "TW"
    WATT = "W"
    YOCTOWATT = "yW"
    YOTTAWATT = "YW"
    ZEPTOWATT = "zW"
    ZETTAWATT = "ZW"


class UnitsPressure(Enum):
    """The units used to represent a pressure."""

    ATMOSPHERE = "atm"
    ATTOPASCAL = "aPa"
    BAR = "bar"
    CENTIBAR = "cbar"
    CENTIPASCAL = "cPa"
    DECAPASCAL = "daPa"
    DECIBAR = "dbar"
    DECIPASCAL = "dPa"
    EXAPASCAL = "EPa"
    FEMTOPASCAL = "fPa"
    GIGAPASCAL = "GPa"
    HECTOPASCAL = "hPa"
    KILOBAR = "kbar"
    KILOPASCAL = "kPa"
    MEGABAR = "Mbar"
    MEGAPASCAL = "MPa"
    MICROPASCAL = "µPa"
    MILLIBAR = "mbar"
    MILLIPASCAL = "mPa"
    MILLITORR = "mTorr"
    MMHG = "mm Hg"
    NANOPASCAL = "nPa"
    PASCAL = "Pa"
    PETAPASCAL = "PPa"
    PICOPASCAL = "pPa"
    PSI = "psi"
    TERAPASCAL = "TPa"
    TORR = "Torr"
    YOCTOPASCAL = "yPa"
    YOTTAPASCAL = "YPa"
    ZEPTOPASCAL = "zPa"
    ZETTAPASCAL = "ZPa"


class UnitsTemperature(Enum):
    """The units used to represent a temperature."""

    CELSIUS = "°C"
    FAHRENHEIT = "°F"
    KELVIN = "K"
    RANKINE = "°R"


class UnitsTime(Enum):
    """The units used to represent a time interval."""

    ATTOSECOND = "as"
    CENTISECOND = "cs"
    DAY = "d"
    DECASECOND = "das"
    DECISECOND = "ds"
    EXASECOND = "Es"
    FEMTOSECOND = "fs"
    GIGASECOND = "Gs"
    HECTOSECOND = "hs"
    HOUR = "h"
    KILOSECOND = "ks"
    MEGASECOND = "Ms"
    MICROSECOND = "µs"
    MILLISECOND = "ms"
    MINUTE = "min"
    NANOSECOND = "ns"
    PETASECOND = "Ps"
    PICOSECOND = "ps"
    SECOND = "s"
    TERASECOND = "Ts"
    YOCTOSECOND = "ys"
    YOTTASECOND = "Ys"
    ZEPTOSECOND = "zs"
    ZETTASECOND = "Zs"


class UniversallyUniqueIdentifier(ConstrainedStr):
    regex = re.compile(
        r"(urn:uuid:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
    )


class AnnotationID(LSID):
    regex = re.compile(
        r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Annotation:\S+)|(Annotation:\S+)"
    )

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v) -> "AnnotationID":
        if not cls.regex.match(v):
            search = cls.regex.search(v)
            if search:
                import warnings

                new_v = search.group()
                warnings.warn(f"Casting invalid AnnotationID {v!r} to {new_v!r}")
                v = new_v
        return v


class ChannelID(LSID):
    regex = re.compile(r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Channel:\S+)|(Channel:\S+)")


class DatasetID(LSID):
    regex = re.compile(r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Dataset:\S+)|(Dataset:\S+)")


class DetectorID(LSID):
    regex = re.compile(
        r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Detector:\S+)|(Detector:\S+)"
    )


class DichroicID(LSID):
    regex = re.compile(
        r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Dichroic:\S+)|(Dichroic:\S+)"
    )


class ExperimenterGroupID(LSID):
    regex = re.compile(
        r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:ExperimenterGroup:\S+)|(ExperimenterGroup:\S+)"
    )


class ExperimenterID(LSID):
    regex = re.compile(
        r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Experimenter:\S+)|(Experimenter:\S+)"
    )


class ExperimentID(LSID):
    regex = re.compile(
        r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Experiment:\S+)|(Experiment:\S+)"
    )


class FilterID(LSID):
    regex = re.compile(r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Filter:\S+)|(Filter:\S+)")


class FilterSetID(LSID):
    regex = re.compile(
        r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:FilterSet:\S+)|(FilterSet:\S+)"
    )


class FolderID(LSID):
    regex = re.compile(r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Folder:\S+)|(Folder:\S+)")


class ImageID(LSID):
    regex = re.compile(r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Image:\S+)|(Image:\S+)")


class InstrumentID(LSID):
    regex = re.compile(
        r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Instrument:\S+)|(Instrument:\S+)"
    )


class LightSourceID(LSID):
    regex = re.compile(
        r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:LightSource:\S+)|(LightSource:\S+)"
    )


class MicrobeamManipulationID(LSID):
    regex = re.compile(
        r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:MicrobeamManipulation:\S+)|(MicrobeamManipulation:\S+)"
    )


class ModuleID(LSID):
    regex = re.compile(r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Module:\S+)|(Module:\S+)")


class ObjectiveID(LSID):
    regex = re.compile(
        r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Objective:\S+)|(Objective:\S+)"
    )


class PixelsID(LSID):
    regex = re.compile(r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Pixels:\S+)|(Pixels:\S+)")


class PlateAcquisitionID(LSID):
    regex = re.compile(
        r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:PlateAcquisition:\S+)|(PlateAcquisition:\S+)"
    )


class PlateID(LSID):
    regex = re.compile(r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Plate:\S+)|(Plate:\S+)")


class ProjectID(LSID):
    regex = re.compile(r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Project:\S+)|(Project:\S+)")


class ReagentID(LSID):
    regex = re.compile(r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Reagent:\S+)|(Reagent:\S+)")


class ROIID(LSID):
    regex = re.compile(r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:\S+)|(\S+)")


class ScreenID(LSID):
    regex = re.compile(r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Screen:\S+)|(Screen:\S+)")


class ShapeID(LSID):
    regex = re.compile(r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Shape:\S+)|(Shape:\S+)")


class WellID(LSID):
    regex = re.compile(r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:Well:\S+)|(Well:\S+)")


class WellSampleID(LSID):
    regex = re.compile(
        r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:WellSample:\S+)|(WellSample:\S+)"
    )
