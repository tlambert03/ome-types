from . import convert_schema

import os

this_dir = os.path.dirname(__file__)
schema = os.path.join(this_dir, "ome.xsd")
target = os.path.join(this_dir, "..", "_model")
convert_schema(schema, target)
