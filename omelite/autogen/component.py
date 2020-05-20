import builtins
from typing import Set

from xmlschema import qnames, validators

from .util import camel_to_snake, make_enum, type_name_lookup


class ComponentConverter:
    def __init__(self, component: validators.XsdComponent):
        self.component = component
        self.local_name = component.local_name or ""
        self.prefixed_name = component.prefixed_name or ""

    @property
    def snake_name(self) -> str:
        return camel_to_snake(self.local_name)

    @property
    def type_string(self) -> str:
        """single type, without Optional, etc..."""
        if self.component.ref is not None:
            name = self.component.ref.local_name
            return name

        type_: validators.XsdType = self.component.type
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
            enum = type_.get_facet(qnames.XSD_ENUMERATION)
            if enum:
                return self.component.local_name
            if type_.base_type.local_name == "string":
                return "str"
        return ""

    def get_locals(self) -> set:
        locals_: Set[str] = set()
        type_: validators.XsdType = getattr(self.component, "type", None)
        if not type_:
            return locals_
        if type_.is_global() or type_.is_complex():
            return locals_
        if type_.is_restriction():
            # enumeration
            if type_.get_facet(qnames.XSD_ENUMERATION):
                locals_.add(make_enum(type_, name=self.component.local_name))
        return locals_

    def get_imports(self, with_types=True) -> set:
        imports: Set[str] = set()
        type_: validators.XsdType = getattr(self.component, "type", None)
        if not type_:
            return imports
        if self.is_optional:
            imports.add("from typing import Optional")
        if type_.is_datetime():
            imports.add("from datetime import datetime")
        if self.component.ref is not None:
            imports.add(f"from . import {self.type_string}")

        if type_.is_global() and with_types:
            pref, name = type_.prefixed_name.split(":")
            if not pref.startswith("xs"):
                imports.add(f"from .types import {self.type_string}")

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
                        default_val = f"{self.type_string}('{default_val}')"
                else:
                    default_val = "None"
            return f" = {default_val}"
        return ""

    @property
    def is_enum(self):
        return self.component.type.get_facet(qnames.XSD_ENUMERATION) is not None

    @property
    def is_optional(self):
        if hasattr(self.component, "min_occurs") and self.component.min_occurs == 0:
            return True
        elif hasattr(self.component, "is_optional") and self.component.is_optional():
            return True
        return False

    def __str__(self) -> str:
        if isinstance(
            self.component, (validators.XsdAnyAttribute, validators.XsdAnyElement)
        ):
            return ""
        return f"{self.snake_name}{self.full_type_string}{self.default_val_str}"
