import builtins
import os
import re
import shutil
from typing import Generator, Iterable, List, Set, Union

import black
import isort
from xmlschema import XMLSchema, qnames
from xmlschema.validators import (
    XsdAnyAttribute,
    XsdAnyElement,
    XsdAttribute,
    XsdElement,
    XsdType,
)

# FIXME: hacks
OVERRIDE = {
    "MetadataOnly": ("bool", "False", None),
    "XMLAnnotation": ("Optional[str]", "None", "from typing import Optional\n\n",),
    "BinData/Length": ("int", None, None),
    "ROI/Union": (
        "conlist(Shape, min_items=1)",
        None,
        "from pydantic.types import conlist\nfrom .shape import Shape",
    ),
    "TiffData/UUID": (
        r'Optional[dataclass(type("UUID", (), {"__annotations__": '
        r'{"file_name": str, "value": UniversallyUniqueIdentifier}}))]',
        None,
        "from typing import Optional\n\nfrom "
        ".simple_types import UniversallyUniqueIdentifier",
    ),
}


def black_format(text, line_length=79):
    return black.format_str(text, mode=black.FileMode(line_length=line_length))


def sort_imports(text):
    return isort.SortImports(file_contents=text).output


def sort_types(el):
    if not el.is_complex() and not el.base_type.is_restriction():
        return "    " + el.local_name.lower()
    return el.local_name.lower()


def sort_prop(prop):
    return ("" if prop.default_val_str else "   ") + prop.format().lower()


def as_identifier(s):
    # Remove invalid characters
    _s = re.sub("[^0-9a-zA-Z_]", "", s)
    # Remove leading characters until we find a letter or underscore
    _s = re.sub("^[^a-zA-Z_]+", "", _s)
    if not _s:
        raise ValueError(f"Could not clean {s}: nothing left")
    return _s


def camel_to_snake(name):
    # https://stackoverflow.com/a/1176023
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower().replace(" ", "_")


def local_import(item_type):
    return f"from .{camel_to_snake(item_type)} import {item_type}"


def make_dataclass(component) -> List[str]:
    lines = ["from pydantic.dataclasses import dataclass", ""]
    if isinstance(component, XsdType):
        base_type = component.base_type
    else:
        base_type = component.type.base_type

    if base_type and not hasattr(base_type, "python_type"):
        base_name = f"({base_type.local_name})"
        if base_type.is_complex():
            lines += [local_import(base_type.local_name)]
        else:
            lines += [f"from .simple_types import {base_type.local_name}"]
    else:
        base_name = ""

    base_members = set()
    _basebase = base_type
    while _basebase:
        base_members.update(set(iter_members(base_type)))
        _basebase = _basebase.base_type

    members = MemberSet(m for m in iter_members(component) if m not in base_members)
    lines += members.imports()
    lines += members.locals()

    cannot_have_required_args = base_type and members.has_non_default_args()
    if cannot_have_required_args:
        lines += ["_no_default = object()", ""]

    lines += ["@dataclass", f"class {component.local_name}{base_name}:"]
    lines += members.lines(
        indent=1,
        force_defaults=" = _no_default  # type: ignore"
        if cannot_have_required_args
        else None,
    )

    if cannot_have_required_args:
        lines += ["", "    # hack for dataclass inheritance with non-default args"]
        lines += ["    # https://stackoverflow.com/a/53085935/"]
        lines += ["    def __post_init__(self):"]
        for m in members.non_defaults:
            lines += [f"        if self.{m.identifier} is _no_default:"]
            lines += [
                "    " * 3 + 'raise TypeError("__init__ missing 1 '
                f'required argument: {m.identifier!r}")'
            ]

    return lines


def make_enum(component, name=None):
    name = name or component.local_name
    lines = ["from enum import Enum", ""]
    lines += [f"class {name}(Enum):"]
    enum_elems = list(component.elem.iter("enum"))
    facets = component.get_facet(qnames.XSD_ENUMERATION)
    members = []
    if enum_elems:
        for el, value in zip(enum_elems, facets.enumeration):
            name = el.attrib["enum"]
            if component.base_type.python_type.__name__ == "str":
                value = f'"{value}"'
            members.append((name, value))
    else:
        for e in facets.enumeration:
            members.append((camel_to_snake(e), repr(e)))

    for n, v in sorted(members):
        lines.append(f"    {as_identifier(n).upper()} = {v}")
    return lines


facet_converters = {
    qnames.XSD_PATTERN: lambda f: [f"regex = re.compile(r'{f.regexps[0]}')"],
    qnames.XSD_MIN_INCLUSIVE: lambda f: [f"ge = {f.value}"],
    qnames.XSD_MIN_EXCLUSIVE: lambda f: [f"gt = {f.value}"],
    qnames.XSD_MAX_INCLUSIVE: lambda f: [f"le = {f.value}"],
    qnames.XSD_MAX_EXCLUSIVE: lambda f: [f"lt = {f.value}"],
    qnames.XSD_LENGTH: lambda f: [f"min_length = {f.value}", f"max_length = {f.value}"],
    qnames.XSD_MIN_LENGTH: lambda f: [f"min_length = {f.value}"],
    qnames.XSD_MAX_LENGTH: lambda f: [f"max_length = {f.value}"],
}


def iter_all_members(component):
    for c in component.iter_components((XsdElement, XsdAttribute)):
        if c is component:
            continue
        yield c


def iter_members(
    component: Union[XsdElement, XsdType]
) -> Generator[Union[XsdElement, XsdAttribute], None, None]:
    if isinstance(component, XsdElement):
        for attr in component.attributes.values():
            if isinstance(attr, XsdAttribute):
                yield attr
        for elem in component.iterchildren():
            yield elem
    else:
        yield from iter_all_members(component)


class Member:
    def __init__(self, component: Union[XsdElement, XsdAttribute]):
        self.component = component
        assert not component.is_global()

    @property
    def identifier(self) -> str:
        if isinstance(self.component, (XsdAnyElement, XsdAnyAttribute)):
            return self.component.local_name
        ident = camel_to_snake(self.component.local_name)
        if not ident.isidentifier():
            raise ValueError(f"failed to make identifier of {self!r}")
        return ident

    @property
    def type(self) -> XsdType:
        return self.component.type

    @property
    def is_enum_type(self) -> bool:
        return self.type.get_facet(qnames.XSD_ENUMERATION) is not None

    @property
    def is_builtin_type(self) -> bool:
        return hasattr(self.type, "python_type")

    @property
    def key(self):
        p = self.component.parent
        name = p.local_name
        while not name and (p.parent is not None):
            p = p.parent
            name = p.local_name
        name = f"{name}/{self.component.local_name}"
        if name not in OVERRIDE and self.component.local_name in OVERRIDE:
            return self.component.local_name
        return name

    def locals(self) -> Set[str]:
        if self.key in OVERRIDE:
            return set()
        if isinstance(self.component, (XsdAnyElement, XsdAnyAttribute)):
            return set()
        if not self.type or self.type.is_global():
            return set()
        locals_: Set[str] = set()
        # FIXME: this bit is mostly hacks
        if self.type.is_complex() and self.component.ref is None:
            locals_.add("\n".join(make_dataclass(self.component)) + "\n")
        if self.type.is_restriction() and self.is_enum_type:
            locals_.add(
                "\n".join(make_enum(self.type, name=self.component.local_name)) + "\n"
            )
        return locals_

    def imports(self) -> Set[str]:
        if self.key in OVERRIDE:
            _imp = OVERRIDE[self.key][2]
            return set([_imp]) if _imp else set()
        if isinstance(self.component, (XsdAnyElement, XsdAnyAttribute)):
            return set(["from typing import Any"])
        imports = set()
        if not self.max_occurs:
            imports.add("from typing import List")
            if self.is_optional:
                imports.add("from dataclasses import field")
        elif self.is_optional:
            imports.add("from typing import Optional")
        if self.type.is_datetime():
            imports.add("from datetime import datetime")
        if not self.is_builtin_type and self.type.is_global():
            # FIXME: hack
            if not self.type.local_name == "anyType":
                if self.type.is_complex():
                    imports.add(local_import(self.type.local_name))
                else:
                    imports.add(f"from .simple_types import {self.type.local_name}")

        if self.component.ref is not None:
            if self.component.ref.local_name not in OVERRIDE:
                imports.add(local_import(self.component.ref.local_name))

        return imports

    @property
    def type_string(self) -> str:
        """single type, without Optional, etc..."""
        if self.key in OVERRIDE:
            return OVERRIDE[self.key][0]
        if isinstance(self.component, (XsdAnyElement, XsdAnyAttribute)):
            return "Any"
        if self.component.ref is not None:
            assert self.component.ref.is_global()
            return self.component.ref.local_name

        if self.type.is_datetime():
            return "datetime"
        if self.is_builtin_type:
            return self.type.python_type.__name__

        if self.type.is_global():
            return self.type.local_name
        elif self.type.is_complex():
            return self.component.local_name

        if self.type.is_restriction():
            # enumeration
            enum = self.type.get_facet(qnames.XSD_ENUMERATION)
            if enum:
                return self.component.local_name
            if self.type.base_type.local_name == "string":
                return "str"
        return ""

    @property
    def full_type_string(self) -> str:
        """full type, like Optional[List[str]]"""
        if self.key in OVERRIDE and self.type_string:
            return f": {self.type_string}"
        type_string = self.type_string
        if not type_string:
            return ""
        if not self.max_occurs:
            type_string = f"List[{type_string}]"
        elif self.is_optional:
            type_string = f"Optional[{type_string}]"
        return f": {type_string}" if type_string else ""

    @property
    def default_val_str(self) -> str:
        if self.key in OVERRIDE:
            default = OVERRIDE[self.key][1]
            return f" = {default}" if default else ""
        if not self.is_optional:
            return ""

        if not self.max_occurs:
            default_val = "field(default_factory=list)"
        else:
            default_val = self.component.default
            if default_val is not None:
                if self.is_enum_type:
                    default_val = f"{self.type_string}('{default_val}')"
                elif hasattr(builtins, self.type_string):
                    default_val = repr(getattr(builtins, self.type_string)(default_val))
            else:
                default_val = "None"
        return f" = {default_val}"

    @property
    def max_occurs(self) -> bool:
        return getattr(self.component, "max_occurs", 1)

    @property
    def is_optional(self) -> bool:
        # FIXME: hack.  doesn't fully capture the restriction
        if getattr(self.component.parent, "model", "") == "choice":
            return True
        if hasattr(self.component, "min_occurs"):
            return self.component.min_occurs == 0
        return self.component.is_optional()

    def __repr__(self) -> str:
        type_ = "element" if isinstance(self.component, XsdElement) else "attribute"
        return f"<Member {type_} {self.component.local_name}>"

    def format(self, force_default=None) -> str:
        default = self.default_val_str
        if force_default:
            default = default or force_default
        return f"{self.identifier}{self.full_type_string}{default}"


class MemberSet:
    def __init__(self, initial: Iterable = ()):
        self._members: Set[Member] = set()
        self.update(initial)

    def add(self, member: Member):
        if not isinstance(member, Member):
            member = Member(member)
        self._members.add(member)

    def update(self, members: Iterable):
        for member in members:
            self.add(member)

    def lines(self, indent=1, force_defaults: str = None) -> List[str]:
        if not self._members:
            lines = ["    " * indent + "pass"]
        else:
            lines = [
                "    " * indent + m.format(force_defaults)
                for m in sorted(self._members, key=lambda x: sort_prop(x))
            ]
        return lines

    def imports(self) -> List[str]:
        if self._members:
            return list(set.union(*[m.imports() for m in self._members]))
        return []

    def locals(self) -> List[str]:
        if self._members:
            return list(set.union(*[m.locals() for m in self._members]))
        return []

    def has_non_default_args(self) -> bool:
        return any(not m.default_val_str for m in self._members)

    @property
    def non_defaults(self) -> "MemberSet":
        return MemberSet(m for m in self._members if not m.default_val_str)

    def __iter__(self):
        return iter(self._members)


class GlobalElem:
    def __init__(self, elem: Union[XsdElement, XsdType]):
        assert elem.is_global()
        self.elem = elem

    @property
    def type(self):
        return self.elem if self.is_type else self.elem.type

    @property
    def is_complex(self):
        if hasattr(self.type, "is_complex"):
            return self.type.is_complex()
        return False

    @property
    def is_element(self):
        return isinstance(self.elem, XsdElement)

    @property
    def is_type(self):
        return isinstance(self.elem, XsdType)

    @property
    def is_enum(self) -> bool:
        is_enum = bool(self.elem.get_facet(qnames.XSD_ENUMERATION) is not None)
        if is_enum:
            if not len(self.elem.facets) == 1:
                raise NotImplementedError("Unexpected enum with multiple facets")
        return is_enum

    def _simple_class(self) -> List[str]:
        if self.is_enum:
            return make_enum(self.elem)

        lines = []
        if self.type.base_type.is_restriction():
            parent = self.type.base_type.local_name
        else:
            # it's a restriction of a builtin
            pytype = self.elem.base_type.python_type.__name__
            parent = f"Constrained{pytype.title()}"
            lines.extend([f"from pydantic.types import {parent}", ""])
        lines.append(f"class {self.elem.local_name}({parent}):")

        members = []
        for key, facet in self.elem.facets.items():
            members.extend([f"    {line}" for line in facet_converters[key](facet)])
        lines.extend(members if members else ["    pass"])
        if any("re.compile" in m for m in members):
            lines = ["import re", ""] + lines
        return lines

    def _abstract_class(self) -> List[str]:
        # FIXME: ? this might be a bit of an OME-schema-specific hack
        # this seems to be how abstract is used in the OME schema
        for e in self.elem.iter_components():
            if e != self.elem:
                raise NotImplementedError(
                    "Don't yet know how to handle abstract class with sub-components"
                )

        subs = [
            el
            for el in self.elem.schema.elements.values()
            if el.substitution_group == self.elem.name
        ]

        if not subs:
            raise NotImplementedError(
                "Don't know how to handle abstract class without substitutionGroups"
            )

        for el in subs:
            if not el.type.is_extension() and el.type.base_type == self.elem.type:
                raise NotImplementedError(
                    "Expected all items in substitution group to extend "
                    f"the type {self.elem.type} of Abstract element {self.elem}"
                )

        sub_names = [el.local_name for el in subs]
        lines = ["from typing import Union"]
        lines.extend([local_import(n) for n in sub_names])
        lines += [local_import(self.elem.type.local_name)]
        lines += [f"{self.elem.local_name} = {self.elem.type.local_name}", ""]
        lines += [f"{self.elem.local_name}Type = Union[{', '.join(sub_names)}]"]
        return lines

    def lines(self) -> str:
        if not self.is_complex:
            lines = self._simple_class()
        elif self.elem.abstract:
            lines = self._abstract_class()
        else:
            lines = make_dataclass(self.elem)
        return "\n".join(lines)

    def format(self) -> str:
        return black_format(sort_imports(self.lines() + "\n"))

    def write(self, filename: str) -> None:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write(self.format())

    @property
    def fname(self) -> str:
        return f"{camel_to_snake(self.elem.local_name)}.py"


_this_dir = os.path.dirname(__file__)
# _url = os.path.join(_this_dir, "ome_types", "ome-2016-06.xsd")
_url = "https://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd"
_target = os.path.join(_this_dir, "ome_types", "model")


def convert_schema(url=_url, target_dir=_target):
    print("Inspecting XML schema ...")
    schema = XMLSchema(url)
    print("Building dataclasses ...")
    shutil.rmtree(target_dir, ignore_errors=True)
    init_imports = []
    simples: List[GlobalElem] = []
    for elem in sorted(schema.types.values(), key=sort_types):
        if elem.local_name in OVERRIDE:
            continue
        converter = GlobalElem(elem)
        if not elem.is_complex():
            simples.append(converter)
            continue
        targetfile = os.path.join(target_dir, converter.fname)
        init_imports.append((converter.fname, elem.local_name))
        converter.write(filename=targetfile)

    for elem in schema.elements.values():
        if elem.local_name in OVERRIDE:
            continue
        converter = GlobalElem(elem)
        targetfile = os.path.join(target_dir, converter.fname)
        init_imports.append((converter.fname, elem.local_name))
        converter.write(filename=targetfile)

    text = "\n".join([s.format() for s in simples])
    text = black_format(sort_imports(text))
    with open(os.path.join(target_dir, "simple_types.py"), "w") as f:
        f.write(text)

    text = ""
    for fname, classname in init_imports:
        text += local_import(classname) + "\n"
    text = sort_imports(text)
    text += f"\n\n__all__ = [{', '.join(sorted(repr(i[1]) for i in init_imports))}]"
    text = black_format(text)
    with open(os.path.join(target_dir, f"__init__.py"), "w") as f:
        f.write(text)


if __name__ == "__main__":
    # for testing
    convert_schema()
