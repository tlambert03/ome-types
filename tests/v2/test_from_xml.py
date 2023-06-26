from pathlib import Path

import pytest

from ome_types2 import from_xml

TESTS = Path(__file__).parent.parent
ALL_XML = list((TESTS / "data").glob("*.ome.xml"))


def true_stem(p: Path) -> str:
    return p.name.partition(".")[0]


@pytest.mark.parametrize("xml", ALL_XML, ids=true_stem)
def test_from_xml(xml):
    print(from_xml(xml))
