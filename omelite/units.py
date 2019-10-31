from enum import Enum
import numpy as np


class UnitsLength(Enum):
    """The units used to represent a length"""

    pm = -12
    nm = -9
    um = -6
    mm = -3
    cm = -2
    dm = -1
    m = 0
    dam = 1
    hm = 2
    km = 3
    Mm = 6
    Gm = 9


class UnitsTime(Enum):
    """The units used to represent a time interval"""

    ps = -12
    ns = -9
    us = -6
    ms = -3
    cs = -2
    ds = -1
    s = 0
    das = 1
    hs = 2
    ks = 3
    Ms = 6
    Gs = 9


class DimensionOrder(str, Enum):
    """The order in which the individual planes of data are interleaved."""

    xyzct = "xyzct"
    xyztc = "xyztc"
    xyctz = "xyctz"
    xyczt = "xyczt"
    xytcz = "xytcz"
    xytzc = "xytzc"


class PixelType(Enum):
    """The number size/kind used to represent a pixel"""

    int8 = np.int8
    int16 = np.int16
    int32 = np.int32
    uint8 = np.uint8
    uint16 = np.uint16
    uint32 = np.uint32
    float = np.float32
    double = np.float64
    complex = np.complex64
    complex_double = np.complex128
    bit = np.bool
