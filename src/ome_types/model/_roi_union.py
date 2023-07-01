from contextlib import suppress
from typing import Iterable, List, MutableSequence, Type, Union, overload

from pydantic import Field, ValidationError, validator

from ome_types._mixins._base_type import OMEType
from ome_types.model.ome_2016_06.ellipse import Ellipse
from ome_types.model.ome_2016_06.label import Label
from ome_types.model.ome_2016_06.line import Line
from ome_types.model.ome_2016_06.mask import Mask
from ome_types.model.ome_2016_06.point import Point
from ome_types.model.ome_2016_06.polygon import Polygon
from ome_types.model.ome_2016_06.polyline import Polyline
from ome_types.model.ome_2016_06.rectangle import Rectangle

_ShapeCls = (Rectangle, Mask, Point, Ellipse, Line, Polyline, Polygon, Label)
ShapeType = Union[Rectangle, Mask, Point, Ellipse, Line, Polyline, Polygon, Label]
_KINDS: dict[str, Type[ShapeType]] = {
    "rectangle": Rectangle,
    "mask": Mask,
    "point": Point,
    "ellipse": Ellipse,
    "line": Line,
    "polyline": Polyline,
    "polygon": Polygon,
    "label": Label,
}


class ShapeUnion(OMEType, MutableSequence[ShapeType]):  # type: ignore[misc]
    # NOTE: in reality, this is List[ShapeGroupType]... but
    # for some reason that messes up xsdata data binding
    __root__: List[object] = Field(
        default_factory=list,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "Label",
                    "type": Label,
                },
                {
                    "name": "Polygon",
                    "type": Polygon,
                },
                {
                    "name": "Polyline",
                    "type": Polyline,
                },
                {
                    "name": "Line",
                    "type": Line,
                },
                {
                    "name": "Ellipse",
                    "type": Ellipse,
                },
                {
                    "name": "Point",
                    "type": Point,
                },
                {
                    "name": "Mask",
                    "type": Mask,
                },
                {
                    "name": "Rectangle",
                    "type": Rectangle,
                },
            ),
        },
    )

    @validator("__root__", each_item=True)
    def _validate_shapes(cls, v: ShapeType) -> ShapeType:
        if isinstance(v, _ShapeCls):
            return v
        if isinstance(v, dict):
            # NOTE: this is here to preserve the v1 behavior of passing a dict like
            # {"kind": "label", "x": 0, "y": 0}
            # to create a label rather than a point
            if "kind" in v:
                kind = v.pop("kind").lower()
                return _KINDS[kind](**v)

            for cls_ in _ShapeCls:
                with suppress(ValidationError):
                    return cls_(**v)
        raise ValueError(f"Invalid shape: {v}")

    def __repr__(self) -> str:
        return repr(self.__root__)

    def __delitem__(self, _idx: int | slice) -> None:
        del self.__root__[_idx]

    @overload
    def __getitem__(self, _idx: int) -> ShapeType:
        ...

    @overload
    def __getitem__(self, _idx: slice) -> List[ShapeType]:
        ...

    def __getitem__(self, _idx: int | slice) -> ShapeType | List[ShapeType]:
        return self.__root__[_idx]  # type: ignore[return-value]

    def __len__(self) -> int:
        return super().__len__()

    @overload
    def __setitem__(self, _idx: int, _val: ShapeType) -> None:
        ...

    @overload
    def __setitem__(self, _idx: slice, _val: Iterable[ShapeType]) -> None:
        ...

    def __setitem__(
        self, _idx: int | slice, _val: ShapeType | Iterable[ShapeType]
    ) -> None:
        self.__root__[_idx] = _val

    def insert(self, index: int, value: ShapeType) -> None:
        self.__root__.insert(index, value)

    # for some reason, without overloading this... append() adds things to the
    # beginning of the list instead of the end
    def append(self, value: ShapeType) -> None:
        self.__root__.append(value)
