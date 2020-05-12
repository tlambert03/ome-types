import builtins
import re
import os
from textwrap import dedent, indent, wrap
from typing import List, Sequence, Set, Tuple

import black
import isort
import xmlschema
from xmlschema.qnames import XSD_ENUMERATION
from xmlschema.validators import (
    XsdAnyAttribute,
    XsdAnyElement,
    XsdAttribute,
    XsdComponent,
    XsdElement,
    XsdType,
)

from omelite.utils import camel_to_snake


def clean(s):
    # Remove invalid characters
    s = re.sub("[^0-9a-zA-Z_]", "", s)
    # Remove leading characters until we find a letter or underscore
    s = re.sub("^[^a-zA-Z_]+", "", s)
    return s


def print_attrs(e):
    for n in dir(e):
        if n.startswith(("_", "tostring")):
            continue
        try:
            m = getattr(e, n)
            if callable(m):
                m = m()
            print(f"{n:20}", m)
        except Exception:
            pass


type_name_lookup = {
    "string": "str",
    "float": "float",
    "double": "float",
    "decimal": "float",
    "dateTime": "datetime",
    "long": "int",
    "int": "int",
    "anyURI": "str",
    "boolean": "bool",
}


def make_enum(name: str, enumeration: List[str]) -> str:
    lines = [f"class {name}(Enum):"]
    for e in enumeration:
        lines.append(f"    {clean(camel_to_snake(e))} = '{e}'")
    return "\n".join(lines)


class ComponentConverter:
    def __init__(self, component: XsdComponent):
        self.component = component
        self.local_name = component.local_name or ""
        self.prefixed_name = component.prefixed_name or ""

    @property
    def snake_name(self) -> str:
        name = camel_to_snake(self.local_name)
        return name[:-4] if name.endswith("_ref") else name

    @property
    def type_string(self) -> str:
        """single type, without Optional, etc..."""
        if self.component.ref is not None:
            name = self.component.ref.local_name
            if name.endswith("Ref"):
                name = name[:-3]
            return name

        type_: XsdType = self.component.type
        if type_.is_datetime():
            return "datetime"
        if type_.is_global():
            pref, name = type_.prefixed_name.split(":")
            if pref.startswith("xs"):
                name = type_name_lookup[name]
                if not hasattr(builtins, name):
                    raise ValueError(f"Uknown type: {name} in {self.component}")
            return name
        if type_.is_restriction():
            # enumeration
            enum = type_.get_facet(XSD_ENUMERATION)
            if enum:
                return self.component.local_name
            if type_.base_type.local_name == "string":
                return "str"
        return ""

    def get_locals(self) -> set:
        locals_: Set[str] = set()
        type_: XsdType = getattr(self.component, "type", None)
        if not type_:
            return locals_
        if type_.is_global() or type_.is_complex():
            return locals_
        if type_.is_restriction():
            # enumeration
            enum = type_.get_facet(XSD_ENUMERATION)
            if enum:
                locals_.add(make_enum(self.component.local_name, enum.enumeration))
        return locals_

    def get_imports(self) -> set:
        imports: Set[str] = set()
        type_: XsdType = getattr(self.component, "type", None)
        if not type_:
            return imports
        if self.is_optional:
            imports.add("from typing import Optional")
        if type_.is_datetime():
            imports.add("from datetime import datetime")
        if self.component.ref is not None:
            imports.add(f"from . import {self.type_string}")

        if type_.is_global():
            pref, name = type_.prefixed_name.split(":")
            if not pref.startswith("xs"):
                imports.add(f"from .types import {self.type_string}")

        if type_.is_restriction():
            enum = type_.get_facet(XSD_ENUMERATION)
            if enum:
                imports.add(f"from enum import Enum")

        return imports

    @property
    def full_type_string(self) -> str:
        """full type, like Optional[List[str]]"""
        type_string = self.type_string
        return f": {type_string}" if type_string else ""

    @property
    def default_val_str(self) -> str:
        if self.is_optional:
            if hasattr(self.component, "max_occurs") and not self.component.max_occurs:
                default_val = "field(default_factory=list)"
            else:
                default_val = self.component.default
                if default_val is not None:
                    if hasattr(builtins, self.type_string):
                        default_val = repr(
                            getattr(builtins, self.type_string)(default_val)
                        )
                    elif self.is_enum:
                        default_val = (
                            f"{self.type_string}.{clean(camel_to_snake(default_val))}"
                        )
                else:
                    default_val = "None"
            return f" = {default_val}"
        return ""

    @property
    def is_enum(self):
        return self.component.type.get_facet(XSD_ENUMERATION) is not None

    @property
    def is_optional(self):
        if hasattr(self.component, "min_occurs") and self.component.min_occurs == 0:
            return True
        elif hasattr(self.component, "is_optional") and self.component.is_optional():
            return True
        return False

    def __str__(self) -> str:
        if isinstance(self.component, (XsdAnyAttribute, XsdAnyElement)):
            return ""
        return f"{self.snake_name}{self.full_type_string}{self.default_val_str}"


class AttributeConverter(ComponentConverter):
    def __init__(self, component: XsdAttribute):
        super().__init__(component)
        self.component = component

    @property
    def full_type_string(self) -> str:
        """full type, like Optional[List[str]]"""
        type_string = self.type_string
        if not type_string:
            return ""
        if self.is_optional:
            type_string = f"Optional[{type_string}]"
        return f": {type_string}" if type_string else ""


class ElementConverter(ComponentConverter):
    def __init__(self, component: XsdElement):
        super().__init__(component)
        self.component = component

    def get_imports(self):
        imports = super().get_imports()
        if not self.component.max_occurs:
            imports.add("from typing import List")

        if self.component.min_occurs == 0:
            if not self.component.max_occurs:
                imports.add("from dataclasses import field")
            else:
                imports.add("from typing import Optional")
        return imports

    @property
    def full_type_string(self) -> str:
        """full type, like Optional[List[str]]"""
        type_string = self.type_string
        if not type_string:
            return ""
        if not self.component.max_occurs:
            type_string = f"List[{type_string}]"
        if self.component.min_occurs == 0 and self.component.max_occurs == 1:
            type_string = f"Optional[{type_string}]"
        return f": {type_string}" if type_string else ""


def props_sorter(props):
    return ("" if "=" in props else "   ") + props.lower()


class ModelConverter(ComponentConverter):
    def __init__(self, component: XsdElement):
        self.component = component
        self.clear()

    def clear(self) -> None:
        self._imports: Set[str] = set(["from dataclasses import dataclass"])
        self._attributes: Set[str] = set()
        self._children: Set[str] = set()
        self._locals: Set[str] = set()

    def gather(self) -> None:
        for attr in self.component.attributes.values():
            atconv = AttributeConverter(attr)
            self._imports.update(atconv.get_imports())
            self._attributes.add(str(atconv))
            self._locals.update(atconv.get_locals())
        for child in self.component.iterchildren():
            elconv = ElementConverter(child)
            self._imports.update(elconv.get_imports())
            self._children.add(str(elconv))
            self._locals.update(elconv.get_locals())

    @property
    def docstring(self) -> str:
        try:
            doc = dedent(self.component.annotation.documentation[0].text)
            doc = "\n".join(wrap(dedent(doc).strip()))
            doc = f'"""{doc}\n"""\n'
            return doc
        except (AttributeError, IndexError):
            return ""

    def dataclass(self) -> str:
        dataclass = "@dataclass\n"
        dataclass += f"class {self.component.local_name}:\n"
        dataclass += indent(self.docstring, "    ")
        members = list(self._attributes) + list(self._children)
        # required attributes at the top
        dataclass += indent("\n".join(sorted(members, key=props_sorter)), "    ")
        return dataclass

    def imports(self) -> str:

        return isort.SortImports(file_contents="\n".join(self._imports)).output

    def locals(self) -> str:
        return "\n".join(self._locals)

    def format(self) -> str:

        self.clear()
        self.gather()

        text = f'"""\nAutogenerated model for {self.component.prefixed_name}\n"""\n'
        text += "\n".join([self.imports(), self.locals(), self.dataclass()])

        try:
            model_text = black.format_str(text, mode=black.FileMode())
        except Exception as e:
            raise ValueError(f"black failed on {self.component.local_name}: {e}")
        return model_text

    def __str__(self) -> str:
        return self.format()


class SchemaConverter:
    def __init__(self, schema: str):
        self.schema = xmlschema.XMLSchema(schema)

    def iter_modules(self, elements: Sequence[str] = []):
        _elems: List[Tuple[str, XsdElement]]
        if elements:
            _elems = [(e, self.schema.elements.get(e)) for e in (elements)]
        else:
            _elems = self.schema.elements.items()
        for name, elem in _elems:
            yield name, elem

    def write(self, target="_model", elements: Sequence[str] = []):
        os.makedirs(target, exist_ok=True)
        inits = []
        for name, elem in self.iter_modules(elements):
            inits.append(elem.local_name)
            with open(os.path.join(target, f"{name.lower()}.py"), "w") as f:
                f.write(str(ModelConverter(elem)))
        text = ""
        for i in inits:
            text += f"from .{i.lower()} import {i}\n"
        text = isort.SortImports(file_contents=text).output

        text += f"\n\n__all__ = [{', '.join(repr(i) for i in inits)}]"
        text = black.format_str(text, mode=black.FileMode())
        with open(os.path.join(target, f"__init__.py"), "w") as f:
            f.write(text)


if __name__ == "__main__":

    SchemaConverter("https://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd").write()
