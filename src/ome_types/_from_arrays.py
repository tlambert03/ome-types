from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from ome_types._mixins._validators import numpy_dtype_to_pixel_type

if TYPE_CHECKING:
    import datetime

    import numpy.typing as npt
    from typing_extensions import Literal, TypedDict, Unpack

    from ome_types.model import (
        Channel_AcquisitionMode,
        Channel_ContrastMethod,
        Channel_IlluminationType,
        Color,
        Image,
        Pixels_DimensionOrder,
        UnitsLength,
        UnitsTime,
    )
    from ome_types.model._color import ColorType

    DimsOrderStr = Literal["XYZCT", "XYZTC", "XYCTZ", "XYCZT", "XYTCZ", "XYTZC"]

    class ImagePixelsKwargs(TypedDict, total=False):
        acquisition_date: datetime.datetime | None
        description: str | None
        name: str | None
        dimension_order: Pixels_DimensionOrder | DimsOrderStr
        physical_size_x: float | None
        physical_size_y: float | None
        physical_size_z: float | None
        physical_size_x_unit: UnitsLength | str
        physical_size_y_unit: UnitsLength | str
        physical_size_z_unit: UnitsLength | str
        time_increment: float | None
        time_increment_unit: UnitsTime | str

    class ChannelKwargs(TypedDict, total=False):
        acquisition_mode: Channel_AcquisitionMode | None | str
        color: Color | ColorType | None
        contrast_method: Channel_ContrastMethod | None | str
        emission_wavelength_unit: UnitsLength | str
        emission_wavelength: float | None
        excitation_wavelength_unit: UnitsLength | str
        excitation_wavelength: float | None
        fluor: str | None
        illumination_type: Channel_IlluminationType | str | None
        name: str | None
        nd_filter: float | None
        pinhole_size_unit: UnitsLength | str
        pinhole_size: float | None
        pockel_cell_setting: int | None

    # same as above, but in {name: Sequence[values]} format
    class ChannelTable(TypedDict, total=False):
        acquisition_mode: Sequence[Channel_AcquisitionMode | None | str]
        color: Sequence[Color | ColorType | None]
        contrast_method: Sequence[Channel_ContrastMethod | None | str]
        emission_wavelength_unit: Sequence[UnitsLength | str]
        emission_wavelength: Sequence[float | None]
        excitation_wavelength_unit: Sequence[UnitsLength | str]
        excitation_wavelength: Sequence[float | None]
        fluor: Sequence[str | None]
        illumination_type: Sequence[Channel_IlluminationType | str | None]
        name: Sequence[str | None]
        nd_filter: Sequence[float | None]
        pinhole_size_unit: Sequence[UnitsLength | str]
        pinhole_size: Sequence[float | None]
        pockel_cell_setting: Sequence[int | None]

    class PlaneKwargs(TypedDict, total=False):
        ...


def ome_image(
    shape: Sequence[int],
    dtype: npt.DTypeLike,
    axes: Sequence[str],
    *,
    channels: Sequence[ChannelKwargs] = (),
    planes: Sequence[PlaneKwargs] = (),
    **img_kwargs: Unpack[ImagePixelsKwargs],
) -> Image:
    from ome_types.model import Channel, Image, Pixels, Plane

    shape = tuple(int(i) for i in shape)
    ndim = len(shape)
    if ndim > 5:
        raise ValueError(f"shape must have at most 5 dimensions, not {ndim}")
    if len(axes) != ndim:
        raise ValueError(f"axes must have length {ndim}, not {len(axes)}")
    axes = tuple(x.upper() for x in axes)

    # pull out the kwargs that belong to Image and Pixels
    _img_kwargs, _pix_kwargs = {}, {}
    for k, v in img_kwargs.items():
        if k in ImagePixelsKwargs.__annotations__:
            _img_kwargs[k] = v
        elif k in Pixels.__annotations__:
            _pix_kwargs[k] = v

    sizes = {f"size_{ax.lower()}": size for ax, size in zip(axes, shape)}
    img = Image(
        pixels=Pixels(
            dimension_order="XYZCT",
            **sizes,
            type=numpy_dtype_to_pixel_type(dtype),
            # big_endian=False,
            # significant_bits=8,
            # bin_data=numpy.zeros(shape, dtype=dtype),
            **_pix_kwargs,
            channels=[Channel(**channel) for channel in channels],
            planes=[Plane(**plane) for plane in planes],
        ),
        **_img_kwargs,
    )
    ...
    # TODO: validate against shape and dtype here
    return img


def ome_image_like(
    array: npt.NDArray, axes: Sequence[str], **img_kwargs: Unpack[ImagePixelsKwargs]
) -> Image:
    return ome_image(shape=array.shape, dtype=array.dtype, axes=axes, **img_kwargs)
