from ._ome_2016_06 import simple_types


def __getattr__(name):
    return getattr(simple_types, name)
