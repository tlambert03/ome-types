from pydantic import Field

from ome_types._autogenerated.ome_2016_06.shape import Shape

__NAMESPACE__ = "http://www.openmicroscopy.org/Schemas/OME/2016-06"


class Ellipse(Shape):
    """A simple ellipse object.

    If rotation is required apply a transformation at the Shape level.

    Attributes
    ----------
    x : float
        The X coordinate of the center of the ellipse. [units pixels]
    y : float
        The Y coordinate of the center of the ellipse. [units pixels]
    radius_x : float
        The horizontal radius of the ellipse. [units pixels]
    radius_y : float
        The vertical radius of the ellipse. [units pixels]
    """

    class Meta:
        namespace = "http://www.openmicroscopy.org/Schemas/OME/2016-06"

    x: float = Field(
        json_schema_extra={
            "name": "X",
            "type": "Attribute",
            "required": True,
        }
    )
    y: float = Field(
        json_schema_extra={
            "name": "Y",
            "type": "Attribute",
            "required": True,
        }
    )
    radius_x: float = Field(
        json_schema_extra={
            "name": "RadiusX",
            "type": "Attribute",
            "required": True,
        }
    )
    radius_y: float = Field(
        json_schema_extra={
            "name": "RadiusY",
            "type": "Attribute",
            "required": True,
        }
    )