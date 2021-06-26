import pint

ureg = pint.UnitRegistry(auto_reduce_dimensions=True)
ureg.define("reference_frame = [_reference_frame]")
ureg.define("@alias grade = gradian")
ureg.define("@alias astronomical_unit = ua")
ureg.define("line = inch / 12")
ureg.define("millitorr = torr / 1000 = mTorr")
ureg.define("@alias torr = Torr")
