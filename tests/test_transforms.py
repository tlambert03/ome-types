from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ome_types import OME, _conversion, from_xml

pytest.importorskip("lxml")

DATA = Path(__file__).parent / "data"


def test_transform() -> None:
    tform = MagicMock(wraps=_conversion._apply_xslt)
    _conversion._apply_xslt = tform
    ome = from_xml(DATA / "2008_instrument.ome.xml")
    assert tform.call_count == 8
    assert isinstance(ome, OME)
    assert ome.instruments[0].microscope.manufacturer == "OME Insturuments"

    with pytest.warns(match="Transformed source"):
        from_xml(DATA / "2008_instrument.ome.xml", warn_on_schema_update=True)
