from pathlib import Path

URI_OME = "http://www.openmicroscopy.org/Schemas/OME/2016-06"
NS_OME = "{" + URI_OME + "}"
NS_XSI = "{http://www.w3.org/2001/XMLSchema-instance}"
SCHEMA_LOC_OME = f"{URI_OME} {URI_OME}/ome.xsd"


OME_2016_06_XSD = str(Path(__file__).parent / "ome-2016-06.xsd")
