from ome_types.model import Line, Rectangle


def test_shape_ids():
    rect = Rectangle(x=0, y=0, width=1, height=1)
    line = Line(x1=0, y1=0, x2=1, y2=1)
    assert rect.id == "Shape:0"
    assert line.id == "Shape:1"
