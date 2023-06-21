from pathlib import Path

import ome_types2
from xsdata.formats.dataclass.parsers.config import ParserConfig


def factory(clazz, params):
    return params
    # return clazz(**params)


# from xsdata.formats.dataclass.parsers.nodes.element
source = Path(__file__).parent / "tests" / "data" / "example.ome.xml"
result = ome_types2.from_xml(
    source, parser_kwargs={"config": ParserConfig(class_factory=factory)}
)

x =1 