import pytest

from ome_types import from_xml, model
from ome_types._mixins import _ids
from ome_types.model import Line, Rectangle


def test_no_id(monkeypatch: "pytest.MonkeyPatch") -> None:
    """Test that ids are optional, and auto-increment."""
    monkeypatch.setattr(_ids, "ID_COUNTER", {})

    i = model.Instrument(id=20)  # type: ignore
    assert i.id == "Instrument:20"
    i2 = model.Instrument()  # type: ignore
    assert i2.id == "Instrument:21"

    # but validation still works
    with pytest.warns(match="Casting invalid InstrumentID"):
        model.Instrument(id="nonsense")


def test_shape_ids(monkeypatch: "pytest.MonkeyPatch") -> None:
    monkeypatch.setattr(_ids, "ID_COUNTER", {})
    rect = Rectangle(x=0, y=0, width=1, height=1)
    line = Line(x1=0, y1=0, x2=1, y2=1)
    assert rect.id == "Shape:0"
    assert line.id == "Shape:1"


def test_id_conversion(monkeypatch: "pytest.MonkeyPatch") -> None:
    """When converting ids, we should still be preserving references."""
    monkeypatch.setattr(_ids, "ID_COUNTER", {})

    XML_WITH_BAD_REFS = """<?xml version="1.0" ?>
    <OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06">
        <Instrument ID="Microscope">
        </Instrument>
        <Image ID="Image:0">
            <InstrumentRef ID="Microscope"/>
            <Pixels BigEndian="false" DimensionOrder="XYCZT" SizeC="3" SizeT="50"
                SizeX="256" SizeY="256" SizeZ="5" ID="Pixels:0" Type="uint16">
            </Pixels>
        </Image>
    </OME>
    """
    with pytest.warns(match="Casting invalid InstrumentID"):
        ome = from_xml(XML_WITH_BAD_REFS)

    assert ome.instruments[0].id == "Instrument:0"
    assert ome.images[0].instrument_ref is not None
    assert ome.images[0].instrument_ref.id == "Instrument:0"
    assert ome.images[0].instrument_ref.ref is ome.instruments[0]
