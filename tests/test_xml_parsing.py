from pathlib import Path

import pytest

from ome_types._lxml import xml2dict

DATA = Path(__file__).parent / "data"


@pytest.mark.parametrize("path", sorted(DATA.glob("*.xml")), ids=lambda p: p.stem)
def test_xml_parse(path):
    xml2dict(path)
