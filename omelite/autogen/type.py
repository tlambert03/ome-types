from textwrap import dedent, indent, wrap
from typing import Set

from xmlschema import qnames, validators

from .attribute import AttributeConverter
from .component import ComponentConverter
from .element import ElementConverter
from .util import (
    black_format,
    facet_converters,
    props_sorter,
    sort_imports,
    type_name_lookup,
    make_enum
)


# TODO: This shares a LOT of duplicated code from ModelConverter ...
# Model should subclass this
class TypeConverter(ComponentConverter):
    def __init__(self, component: validators.XsdType):
        self.component = component

    def clear(self) -> None:
        self._imports: Set[str] = set(["from pydantic.dataclasses import dataclass "])
        self._attributes: Set[AttributeConverter] = set()
        self._children: Set[ElementConverter] = set()
        self._locals: Set[str] = set()

    def gather(self) -> None:
        if self.is_extension and self.component.base_type.is_complex():
            base_attrs = self.component.base_type.attributes
        else:
            base_attrs = []

        for attr in self.component.attributes.values():
            if attr.local_name in base_attrs:
                continue
            atconv = AttributeConverter(attr)
            self._imports.update(atconv.get_imports(with_types=False))
            self._attributes.add(atconv)
            self._locals.update(atconv.get_locals())

        if self.component.content_type.parent is not None:
            for child in self.component.content_type.iter_components():
                if not isinstance(child, validators.XsdElement):
                    continue
                elconv = ElementConverter(child)
                self._imports.update(elconv.get_imports())
                self._children.add(elconv)
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
        base_type = self.component.base_type
        base = f"({base_type.local_name})" if base_type else ""
        dataclass += f"class {self.component.local_name}{base}:\n"
        dataclass += indent(self.docstring, "    ")
        members = list(map(str, self._attributes)) + list(map(str, self._children))
        # required attributes at the top
        dataclass += indent("\n".join(sorted(members, key=props_sorter)), "    ")
        return dataclass

    def imports(self) -> str:
        return "\n".join(self._imports)

    def locals(self) -> str:
        return "\n".join(self._locals)

    def format(self) -> str:

        self.clear()
        self.gather()

        text = "\n".join([self.imports(), self.locals(), self.dataclass()])

        text = sort_imports(text)

        try:
            model_text = black_format(text)
        except Exception as e:
            raise ValueError(f"black failed on {self.component.local_name}: {e}")
        return model_text

    def __str__(self) -> str:
        return self.format()

    @property
    def is_extension(self) -> bool:
        return self.component.is_extension()

    @property
    def is_simple(self):
        return self.component.is_simple()

    @property
    def is_restriction(self):
        return self.component.is_restriction()

    @property
    def base_is_builtin(self):
        return isinstance(self.component.base_type, validators.XsdAtomicBuiltin)

    @property
    def is_enum(self):
        return self.component.get_facet(qnames.XSD_ENUMERATION) is not None

    def convert(self):
        if self.is_enum:
            return make_enum(self.component)

        if self.is_simple:
            if self.is_restriction:
                if "binary" in self.component.base_type.local_name.lower():
                    return ""
                else:
                    return self.make_simple_constrained_class()
        else:
            return self.make_complex_class()

    def make_complex_class(self):
        return self.format()

    def make_simple_constrained_class(self):
        lines = []
        if self.base_is_builtin:
            type_ = type_name_lookup[self.component.base_type.local_name]
            parent = f"Constrained{type_.title()}"
            lines.append(f"from pydantic.types import {parent}")
        else:
            parent = self.component.base_type.local_name
        lines.extend(["", ""])
        lines.append(f"class {self.component.local_name}({parent}):")
        members = []
        for key, facet in self.component.facets.items():
            members.append(f"    {facet_converters[key](facet)}")
        lines.extend(members if members else ["    pass"])
        out = "\n".join(lines) + "\n"
        if "re.compile" in out:
            out = "import re\n\n" + out
        return out
