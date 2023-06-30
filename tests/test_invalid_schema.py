from pathlib import Path

import pytest

from ome_types import from_xml

TESTS = Path(__file__).parent
DATA = TESTS / "data"


def test_bad_xml_annotation() -> None:
    """Test that a bad XML annotation is not imported"""
    with pytest.warns(match="Casting invalid AnnotationID"):
        ome = from_xml(DATA / "invalid_xml_annotation.ome.xml")
    assert len(ome.images) == 1
    assert ome.structured_annotations
    assert ome.structured_annotations[0].id == "Annotation:0"
