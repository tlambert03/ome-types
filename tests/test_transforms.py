from pathlib import Path
from unittest.mock import MagicMock

from ome_types import OME, _conversion, from_xml

DATA = Path(__file__).parent / "data"


def test_transform():
    tform = MagicMock(wraps=_conversion._apply_xslt)
    _conversion._apply_xslt = tform
    ome = from_xml(DATA / "2008_instrument.ome.xml")
    assert tform.call_count == 8
    assert isinstance(ome, OME)
    assert ome.instruments[0].microscope.manufacturer == "OME Insturuments"
