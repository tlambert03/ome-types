from pathlib import Path
from unittest.mock import MagicMock

import pytest
from some_types import SOME, _conversion, from_xml

pytest.importorskip("lxml")

DATA = Path(__file__).parent / "data"


def test_transform() -> None:
    tform = MagicMock(wraps=_conversion._apply_xslt)
    _conversion._apply_xslt = tform
    some = from_xml(DATA / "2008_instrument.some.xml")
    assert tform.call_count == 8
    assert isinstance(some, SOME)
    assert some.instruments[0].microscope.manufacturer == "SOME Insturuments"

    with pytest.warns(match="Transformed source"):
        from_xml(DATA / "2008_instrument.some.xml", warn_on_schema_update=True)
