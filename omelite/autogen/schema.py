import os
from typing import List, Sequence, Tuple

from xmlschema import XMLSchema, validators

from .model import ModelConverter
from .type import TypeConverter
from .util import black_format, sort_imports


class SchemaConverter:
    def __init__(self, schema: str):
        self.schema = XMLSchema(schema)

    def iter_modules(self, elements: Sequence[str] = []):
        _elems: List[Tuple[str, validators.XsdElement]]
        if elements:
            _elems = [(e, self.schema.elements.get(e)) for e in (elements)]
        else:
            _elems = self.schema.elements.items()
        for name, elem in _elems:
            yield name, elem

    def write_models(self, target="_model", elements: Sequence[str] = []):
        inits = []
        for name, elem in self.iter_modules(elements):
            inits.append(elem.local_name)
            with open(os.path.join(target, f"{name.lower()}.py"), "w") as f:
                f.write(str(ModelConverter(elem)))
        text = ""
        for i in inits:
            text += f"from .{i.lower()} import {i}\n"
        text = sort_imports(text)

        text += f"\n\n__all__ = [{', '.join(sorted(repr(i) for i in inits))}]"
        text = black_format(text)
        with open(os.path.join(target, f"__init__.py"), "w") as f:
            f.write(text)

    def _write_types(self, dir):
        text = ""
        for name, elem in self.schema.types.items():
            type_conv = TypeConverter(elem)
            text += type_conv.convert()

        text = sort_imports(text)
        text = black_format(text)

        with open(os.path.join(dir, "types.py"), "w") as f:
            f.write(text)

    def write(self, target="_model", elements: Sequence[str] = []):
        os.makedirs(target, exist_ok=True)
        self.write_models(target=target, elements=elements)
        self._write_types(dir=target)
