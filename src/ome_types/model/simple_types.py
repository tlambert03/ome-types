from ome_types.model.ome_2016_06 import (
    Binning,
    Marker,
    NamingConvention,
    PixelType,
    UnitsElectricPotential,
    UnitsFrequency,
    UnitsLength,
    UnitsPower,
    UnitsPressure,
    UnitsTemperature,
    UnitsTime,
)
from ome_types.model.ome_2016_06 import (
    Shape_FontFamily as FontFamily,
)

__all__ = [
    "PixelType",
    "Binning",
    "FontFamily",
    "Hex40",
    "LSID",
    "Marker",
    "Color",
    "NamingConvention",
    "NonNegativeFloat",
    "NonNegativeInt",
    "NonNegativeLong",
    "PercentFraction",
    "PixelType",
    "PositiveFloat",
    "PositiveInt",
    "UnitsAngle",
    "UnitsElectricPotential",
    "UnitsFrequency",
    "UnitsLength",
    "UnitsPower",
    "UnitsPressure",
    "UnitsTemperature",
    "UnitsTime",
    "UniversallyUniqueIdentifier",
    "AnnotationID",
    "ChannelID",
    "DatasetID",
    "DetectorID",
    "DichroicID",
    "ExperimenterGroupID",
    "ExperimenterID",
    "ExperimentID",
    "FilterID",
    "FilterSetID",
    "FolderID",
    "ImageID",
    "InstrumentID",
    "LightSourceID",
    "MicrobeamManipulationID",
    "ModuleID",
    "ObjectiveID",
    "PixelsID",
    "PlateAcquisitionID",
    "PlateID",
    "ProjectID",
    "ReagentID",
    "ROIID",
    "ScreenID",
    "ShapeID",
    "WellID",
    "WellSampleID",
]


Color = int  # TODO
Hex40 = bytes
NonNegativeFloat = float
NonNegativeInt = int
NonNegativeLong = int
PercentFraction = float
PositiveFloat = float
PositiveInt = int
UnitsAngle = str
UniversallyUniqueIdentifier = str

# IDs

LSID = str
AnnotationID = str
ChannelID = str
DatasetID = str
DetectorID = str
DichroicID = str
ExperimenterGroupID = str
ExperimenterID = str
ExperimentID = str
FilterID = str
FilterSetID = str
FolderID = str
ImageID = str
InstrumentID = str
LightSourceID = str
MicrobeamManipulationID = str
ModuleID = str
ObjectiveID = str
PixelsID = str
ROIID = str
PlateAcquisitionID = str
PlateID = str
ProjectID = str
ReagentID = str
ScreenID = str
ShapeID = str
WellID = str
WellSampleID = str
