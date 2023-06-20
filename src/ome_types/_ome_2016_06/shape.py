from enum import Enum
from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .affine_transform import AffineTransform
from .annotation_ref import AnnotationRef
from .simple_types import Color, NonNegativeInt, ShapeID, UnitsLength


class FillRule(Enum):
    EVEN_ODD = "EvenOdd"
    NON_ZERO = "NonZero"


class FontFamily(Enum):
    CURSIVE = "cursive"
    FANTASY = "fantasy"
    MONOSPACE = "monospace"
    SANSSERIF = "sans-serif"
    SERIF = "serif"


class FontStyle(Enum):
    BOLD = "Bold"
    BOLD_ITALIC = "BoldItalic"
    ITALIC = "Italic"
    NORMAL = "Normal"


class Shape(OMEType):
    """The shape element contains a single specific ROI shape and links that to any
    channels, and a timepoint and a z-section.

    It also records any transform applied to the ROI shape.

    Parameters
    ----------
    id : ShapeID
    annotation_ref : AnnotationRef, optional
    fill_color : Color, optional
        The color of the fill - encoded as RGBA The value "-1" is #FFFFFFFF so
        solid white (it is a signed 32 bit value) NOTE: Prior to the 2012-06
        schema the default value was incorrect and produced a transparent red
        not solid white.
    fill_rule : FillRule, optional
    font_family : FontFamily, optional
    font_size : NonNegativeInt, optional
        Size of the font. Units are set by FontSizeUnit.
    font_size_unit : UnitsLength, optional
        The units used for the font size.
    font_style : FontStyle, optional
    locked : bool, optional
        Controls whether the shape is locked and read only, true is locked,
        false is editable.
    stroke_color : Color, optional
        The color of the stroke  - encoded as RGBA The value "-1" is #FFFFFFFF
        so solid white (it is a signed 32 bit value) NOTE: Prior to the
        2012-06 schema the default value was incorrect and produced a
        transparent red not solid white.
    stroke_dash_array : str, optional
        e.g. "none", "10 20 30 10"
    stroke_width : float, optional
        The width of the stroke. Units are set by StrokeWidthUnit.
    stroke_width_unit : UnitsLength, optional
        The units used for the stroke width.
    text : str, optional
    the_c : NonNegativeInt, optional
        The channel the ROI applies to. If not specified then the ROI applies
        to all the channels of the image. This is numbered from 0.
    the_t : NonNegativeInt, optional
        The timepoint the ROI applies to. If not specified then the ROI
        applies to all the timepoints of the image. This is numbered from 0.
    the_z : NonNegativeInt, optional
        The z-section the ROI applies to. If not specified then the ROI
        applies to all the z-sections of the image. This is numbered from 0.
    transform : AffineTransform, optional
        This is a matrix used to transform the shape. The element has 6
        xsd:float attributes. If the element is present then all 6 values must
        be included.
    """

    id: ShapeID
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    fill_color: Optional[Color] = None
    fill_rule: Optional[FillRule] = None
    font_family: Optional[FontFamily] = None
    font_size: Optional[NonNegativeInt] = None
    font_size_unit: Optional[UnitsLength] = UnitsLength("pt")
    font_style: Optional[FontStyle] = None
    locked: Optional[bool] = None
    stroke_color: Optional[Color] = None
    stroke_dash_array: Optional[str] = None
    stroke_width: Optional[float] = None
    stroke_width_unit: Optional[UnitsLength] = UnitsLength("pixel")
    text: Optional[str] = None
    the_c: Optional[NonNegativeInt] = None
    the_t: Optional[NonNegativeInt] = None
    the_z: Optional[NonNegativeInt] = None
    transform: Optional[AffineTransform] = None
