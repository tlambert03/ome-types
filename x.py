from rich import print

import ome_types
from ome_types.model import MapAnnotation

ome_test = ome_types.OME()

my_dict = data = {
    "uiWidth": "1608",
    "uiWidthBytes": 1,
    "uiHeight": 1608,
    "uiComp": "1",
    "uiBpcInMemory": "16",
}


ome_test.structured_annotations.append(MapAnnotation(value=data))

print(ome_test.to_xml())
print(ome_test.dict())
