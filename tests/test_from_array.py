import numpy as np

from ome_types import model
from ome_types._from_arrays import ome_image_like


def test_ome_image() -> None:
    data = np.empty((2, 2, 3, 10, 20, 3), dtype=np.uint16)

    NAMES = ["a", "b", "c", "d"]  # note, it's actually 1 too many

    img = ome_image_like(
        data,
        description="test",
        channels={"name": NAMES, "color": "red"},
        planes={"position_x": [1] * 12, "exposure_time": 3},
    )

    assert isinstance(img, model.Image)
    assert img.description == "test"
    assert len(img.pixels.channels) == 3
    assert img.pixels.dimension_order == model.Pixels_DimensionOrder.XYCZT
    assert img.pixels.type == model.PixelType.UINT16

    for c, name in zip(img.pixels.channels, NAMES):
        assert c.color == model.Color("red")
        assert c.name == name

    n_planes = np.prod(data.shape[:3])
    assert len(img.pixels.planes) == n_planes
    for p in img.pixels.planes:
        assert p.position_x == 1.0
        assert p.exposure_time == 3.0
