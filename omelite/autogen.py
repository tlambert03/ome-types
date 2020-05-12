from textwrap import dedent
from typing import Any, List, NamedTuple, Optional, Set, Tuple, Union
from ast import literal_eval

import xmlschema
from xmlschema.validators import (
    XsdAnyAttribute,
    XsdAnyElement,
    XsdAttribute,
    XsdElement,
    XsdType,
)

from omelite.utils import camel_to_snake


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


# def walk(node: xmlschema.validators.elements.XsdElement, level=0):
#     print("  " * level + (node.local_name or ""))
#     for attr in node.attributes:
#         print(("  " * (level + 1)) + (attr or ""))
#     for child in node.iterchildren():
#         walk(child, level + 1)


# def _get_type_string(attr):
#     if hasattr(attr, "type"):
#         if attr.type.is_complex() and attr.ref is not None:
#             return attr.ref.prefixed_name
#         else:
#             return attr.type.prefixed_name
#     else:
#         return "[no type]"


# def _list_children(elem):
#     for attr_name, attr in elem.attributes.items():
#         print(f"  {attr_name or ''}: {_get_type_string(attr)}")
#     for child in elem.iterchildren():
#         print(f"  {child.local_name or ''}: {_get_type_string(child)}")


# def get_types(schema: xmlschema.XMLSchema):
#     for name, elem in sorted(schema.elements.items()):
#         print(name)
#         _list_children(elem)
#         print()

type_name_lookup = {
    "string": "str",
    "boolean": "bool",
    "dateTime": "datetime",
    "decimal": "float",
    "Hex40": "_hashlib.HASH",
    "anyURI": "str",
    "long": "int",
    "double": "float",
}


def format_name(name: str) -> str:
    name = camel_to_snake(name)
    return name[:-4] if name.endswith("_ref") else name


# class Attribute(NamedTuple):
#     name: str
#     required: bool
#     namespace: str
#     type_: XsdType
#     doc: str

#     def format_type(self, elem: XsdElement, required: bool = False) -> str:
#         glbl = elem.get_global()
#         type_name = glbl.local_name
#         return type_name_lookup.get(type_name, type_name)

#     def format(self):
#         type_string = self.format_type(self.type_, self.required)
#         return f"{format_name(self.name)}: {type_string}"

#     @classmethod
#     def from_elem(cls, elem: XsdAttribute) -> "Attribute":
#         if isinstance(elem, XsdAnyAttribute):
#             return cls("Any", False, "http://www.w3.org/2001/XMLSchema", Any, "")
#         return cls(
#             elem.local_name,
#             not elem.is_optional(),
#             elem.target_namespace,
#             elem.type,
#             _get_doc(elem),
#         )


# class Child(NamedTuple):
#     name: str
#     min_occurs: int
#     max_occurs: Optional[int]
#     namespace: str
#     type_: XsdType
#     doc: str
#     ref: Optional[XsdElement]

#     def format_type(self) -> str:
#         if self.ref is not None:
#             type_name = self.ref.local_name
#             if type_name.endswith("Ref"):
#                 type_name = type_name[:-3]
#         else:
#             print(self.name, self.type_)
#             type_name = self.type_.local_name or self.type_.base_type.local_name
#         type_name = type_name_lookup.get(type_name, type_name)

#         if not self.max_occurs:
#             type_name = f"List[{type_name}]"
#         if self.min_occurs == 0:
#             type_name = f"Optional[{type_name}]"
#         return type_name

#     def format(self):
#         type_string = self.format_type()
#         return f"{format_name(self.name)}: {type_string}"

#     @classmethod
#     def from_elem(cls, elem: XsdElement) -> "Child":
#         if isinstance(elem, XsdAnyElement):
#             return cls(
#                 "Any", 0, None, "http://www.w3.org/2001/XMLSchema", Any, "", None
#             )
#         return cls(
#             elem.local_name,
#             elem.min_occurs,
#             elem.max_occurs,
#             elem.target_namespace,
#             elem.type,
#             _get_doc(elem),
#             elem.ref,
#         )


# class Model(NamedTuple):
#     name: str
#     attributes: List[Attribute]
#     children: List[Child]


def _get_doc(elem) -> str:
    try:
        return dedent(elem.annotation.documentation[0].text).strip()
    except Exception:
        return ""


# def gather_model(elem: XsdElement) -> Model:
#     name = elem.local_name
#     attrs = [Attribute.from_elem(attr) for attr in elem.attributes.values()]
#     children = [Child.from_elem(child) for child in elem.iterchildren()]
#     return Model(name, attrs, children)


# def gen_model(schema, prefix="OME"):
#     models = []
#     for name, elem in sorted(schema.elements.items()):
#         if prefix and not elem.prefixed_name.startswith(prefix):
#             continue
#         models.append(gather_model(elem))
#     return models


def format_child_elem(child: XsdElement) -> Tuple[str, List[str]]:
    imports: List[str] = []
    if isinstance(child, XsdAnyElement):
        return "Any", []

    if child.ref is not None:
        type_string = child.ref.local_name
        if type_string.endswith("Ref"):
            type_string = type_string[:-3]
        imports.append(f"from . import {type_string}")
    elif child.local_name == "BinaryOnly":
        # FIXME:
        type_string = "BinaryOnly"
    else:
        type_string = child.type.local_name or child.type.base_type.local_name
        type_string = type_name_lookup.get(type_string, type_string)
        if "datetime" in type_string:
            imports.append("from datetime import datetime")
        elif "_hashlib" in type_string:
            imports.append("import _hashlib")
        elif "OME" in child.type.target_namespace:
            imports.append(f"from .types import {type_string}")
        else:
            import builtins

            assert hasattr(
                builtins, type_string
            ), f"Uknown type: {type_string} in {child}"

    if not type_string:
        raise NotImplementedError(f"No type_string for {child}")
    if not child.max_occurs:
        type_string = f"List[{type_string}]"
        imports.append(f"from typing import List")
    elif child.max_occurs != 1:
        raise NotImplementedError(f"Can't handle maxOccurs = {child.max_occurs}")

    default_val = None
    required = False
    if child.min_occurs == 0:
        if not child.max_occurs:
            default_val = "field(default_factory=list)"
            imports.append("from dataclasses import field")
        else:
            type_string = f"Optional[{type_string}]"
            imports.append("from typing import Optional")
    elif child.min_occurs == 1:
        required = True
    else:
        raise NotImplementedError(f"Can't handle minOccurs = {child.min_occurs}")

    default_val = default_val or child.default
    if not default_val and not required:
        default_val = "None"

    type_string = f": {type_string}" if type_string else ""
    if default_val:
        type_string += f" = {default_val}"
    line = f"{format_name(child.local_name)}{type_string}"
    return line, imports


def format_attribute(child: XsdAttribute) -> Tuple[str, List[str]]:
    imports: List[str] = []
    if isinstance(child, XsdAnyAttribute):
        return "Any", []

    if child.ref is not None:
        if child.type.is_simple():
            raise NotImplementedError(
                f"figure out what to do with attr.ref that is simple: {child}"
            )
        type_string = child.ref.local_name
        if type_string.endswith("Ref"):
            type_string = type_string[:-3]
        imports.append(f"from . import {type_string}")
    else:
        type_string = child.type.local_name
        if child.type.is_restriction():
            if "OME" not in child.type.target_namespace:
                raise NotImplementedError(
                    f"Non OME restriction!: {child}, {child.type}"
                )
            imports.append(f"from .types import {type_string}")
        else:
            type_string = type_name_lookup.get(type_string, type_string)
            if not type_string:
                raise NotImplementedError(f"No type_string for {child}")
            if "datetime" in type_string:
                imports.append("from datetime import datetime")
            else:
                import builtins

                assert hasattr(builtins, type_string), f"Uknown type: {type_string}"

    if child.is_optional():
        type_string = f"Optional[{type_string}]"
        imports.append("from typing import Optional")

    default_val = child.default
    if default_val is None and child.is_optional():
        default_val = "None"

    type_string = f": {type_string}" if type_string else ""
    if default_val:
        try:
            default_val = literal_eval(default_val)
        except Exception:
            default_val = f"{'default_val'}"
        type_string += f" = {default_val}"
    line = f"{format_name(child.local_name)}{type_string}"
    return line, imports


def get_props_lines(elem: XsdElement) -> Tuple[List[str], Set[str]]:
    lines: List[str] = []
    imports: Set[str] = set()
    for attr in elem.attributes.values():
        line, imps = format_attribute(attr)
        lines.append(line)
        imports.update(imps)
    for child in elem.iterchildren():
        line, imps = format_child_elem(child)
        lines.append(line)
        imports.update(imps)
    return lines, imports


def props_sorter(props):
    return ("" if "=" in props else "   ") + props.lower()


def format_model(model: XsdElement):
    import black
    import isort

    imports = set(["from dataclasses import dataclass"])
    lines = ["", "", "@dataclass", f"class {model.local_name}:"]

    props_lines, imps = get_props_lines(model)
    imports.update(imps)
    lines.extend(["\t" + i for i in sorted(props_lines, key=props_sorter)])
    model_text = isort.SortImports(file_contents="\n".join(imports)).output
    model_text += "\n".join(lines)
    try:
        model_text = black.format_str(model_text, mode=black.FileMode())
    except Exception as e:
        raise ValueError(f"black failed on {model.local_name}: {e}")
    return model_text


if __name__ == "__main__":
    import os
    import itertools

    schema = xmlschema.XMLSchema("omelite/ome.xsd")

    # print(format_model(schema.elements.get("Experiment")))

    # target_dir = "_model"
    # os.makedirs(target_dir, exist_ok=True)

    # for name, elem in schema.elements.items():
    #     try:
    #         text = format_model(elem)
    #     except Exception as e:
    #         print(e, "in ", name)

    def simple_local_type(i):
        if i.type.is_list():
            pass

    def get_type(i: Union[XsdAttribute, XsdElement]):
        if hasattr(i, "type"):
            simp = "simple" if i.type.is_simple() else "complex"
            locl = "global" if i.type.is_global() else "local"
            lst = "list" if i.type.is_list() else ""
            restr = "restr" if i.type.is_restriction() else ""

            if i.type.is_global():
                return
                name = i.type.local_name
            else:
                if i.type.is_simple():
                    name = i.type
                else:
                    return
                    name = ""
            return f"{simp:8}{locl:9}{lst:6}{restr:7}{name}"

    items = schema.elements.items()
    # items = [(e, schema.elements.get(e)) for e in ("Experiment")]

    def get_row(i):
        if hasattr(i, "type"):
            return {
                "simple": "simple" if i.type.is_simple() else "complex",
                "global": "global" if i.type.is_global() else "local",
                "restriction": "restriction" if i.type.is_restriction() else "",
                "extension": "extension" if i.type.is_extension() else "",
                "atomic": "atomic" if i.type.is_atomic() else "",
                "list": "list" if i.type.is_list() else "",
                "local_name": i.type.local_name,
                "prefixed_name": i.type.prefixed_name,
                # "primitive": i.type.primitive_type
            }
        return {}

    rows = []
    for name, elem in items:
        for i in itertools.chain(elem.attributes.values(), elem.iterchildren()):
            attr = "attr" if isinstance(i, XsdAttribute) else "child"
            # print(f"{attr:8}{name:20}{str(i.local_name):25}", get_type(i))
            row = {'model': name, 'attr': attr, 'name': i.local_name}
            row.update(get_row(i))
            rows.append(row)

    import pandas as pd

    df = pd.DataFrame(rows)
    df.to_csv('~/Desktop/types.csv')
    print(rows)

# if i.type.is_global() ... then i.type.local_name is not None
# otherwise it is none

# all XsdAttribute types are simple ... but can be either local or global
# XsdElements can be all combinations of simple/complex, local/global
