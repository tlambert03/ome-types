import pickle
from pathlib import Path

import pytest

from ome_types import from_xml
from ome_types.model import OME, Channel, Image, Pixels


@pytest.mark.parametrize("channel_kwargs", [{}, {"color": "blue"}])
def test_color_unset(channel_kwargs: dict) -> None:
    ome = OME(
        images=[
            Image(
                pixels=Pixels(
                    size_c=1,
                    size_t=1,
                    size_x=1,
                    size_y=1,
                    size_z=1,
                    dimension_order="XYZTC",
                    type="uint16",
                    channels=[Channel(**channel_kwargs)],
                )
            )
        ]
    )

    assert ("Color" in ome.to_xml()) is bool(channel_kwargs)


def test_serialization(valid_xml: Path) -> None:
    """Test pickle serialization and reserialization."""
    ome = from_xml(valid_xml)
    serialized = pickle.dumps(ome)
    deserialized = pickle.loads(serialized)
    assert ome == deserialized
