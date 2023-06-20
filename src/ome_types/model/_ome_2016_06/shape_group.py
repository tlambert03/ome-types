from typing import Union

from .ellipse import Ellipse
from .label import Label
from .line import Line
from .mask import Mask
from .point import Point
from .polygon import Polygon
from .polyline import Polyline
from .rectangle import Rectangle
from .shape import Shape

ShapeGroup = Shape

ShapeGroupType = Union[Rectangle, Mask, Point, Ellipse, Line, Polyline, Polygon, Label]
