from pathlib import Path

import pydantic
import pytest

from ome_types2 import OME, from_xml

TESTS = Path(__file__).parent.parent
ALL_XML = list((TESTS / "data").glob("*.ome.xml"))
INVALID = {"bad", "invalid_xml_annotation"}


def true_stem(p: Path) -> str:
    return p.name.partition(".")[0]


@pytest.mark.filterwarnings("ignore::ResourceWarning")  # FIXME
@pytest.mark.parametrize("xml", ALL_XML, ids=true_stem)
def test_from_xml(xml: Path) -> None:
    if true_stem(xml) in INVALID:
        with pytest.raises(pydantic.ValidationError):
            from_xml(xml)
    else:
        assert isinstance(from_xml(xml), OME)
