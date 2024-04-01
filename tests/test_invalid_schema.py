from pathlib import Path

import pytest
from some_types import from_xml

TESTS = Path(__file__).parent
DATA = TESTS / "data"


def test_bad_xml_annotation() -> None:
    """Test that a bad XML annotation is not imported"""
    with pytest.warns(match="Casting invalid AnnotationID"):
        some = from_xml(DATA / "invalid_xml_annotation.some.xml")
    assert len(some.images) == 1
    assert some.structured_annotations
    assert some.structured_annotations[0].id == "Annotation:0"
