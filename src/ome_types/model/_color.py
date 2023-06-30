from typing import Any

from pydantic import color
from xsdata.formats.converter import Converter, converter

__all__ = ["Color"]


class Color(color.Color):
    def __init__(self, val: color.ColorType = -1) -> None:
        try:
            val_int = int(val)  # type: ignore
        except ValueError:
            pass
        else:
            val = self._int2tuple(val_int)
        super().__init__(val)

    @classmethod
    def _int2tuple(cls, val: int) -> tuple[int, int, int, float]:
        return (val >> 24 & 255, val >> 16 & 255, val >> 8 & 255, (val & 255) / 255)

    def as_int32(self) -> int:
        r, g, b, *a = self.as_rgb_tuple()
        v = r << 24 | g << 16 | b << 8 | int((a[0] if a else 1) * 255)
        if v < 2**32 // 2:
            return v
        return v - 2**32

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Color):
            return self.as_int32() == o.as_int32()
        return False

    def __int__(self) -> int:
        return self.as_int32()


class ColorConverter(Converter):
    def serialize(self, value: Color, **kwargs: Any) -> str:
        return str(value.as_int32())

    def deserialize(self, value: Any, **kwargs: Any) -> Color:
        return Color(value)


converter.register_converter(Color, ColorConverter())
