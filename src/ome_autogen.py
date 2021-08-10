from __future__ import annotations

import builtins
import os
import re
import shutil
from dataclasses import dataclass, field
from itertools import chain
from pathlib import Path
from textwrap import dedent, indent, wrap
from typing import (
    Any,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

import black
import isort.api
from autoflake import fix_code
from numpydoc.docscrape import NumpyDocString, Parameter
from xmlschema import XMLSchema
from xmlschema.validators import (
    XsdAnyAttribute,
    XsdAnyElement,
    XsdAttribute,
    XsdComponent,
    XsdElement,
    XsdType,
)

try:
    # xmlschema ≥ v1.4.0
    from xmlschema import names as qnames
except ImportError:
    from xmlschema import qnames


# Track all camel-to-snake and pluralization results so we can include them in the model.
camel_snake_registry: Dict[str, str] = {}
plural_registry: Dict[Tuple[str, str], str] = {}


# FIXME: Work out a better way to implement these override hacks.


@dataclass
class Override:
    type_: str
    default: Optional[str] = None
    imports: Optional[str] = None
    body: Optional[str] = None

    def __post_init__(self) -> None:
        if self.imports:
            self.imports = dedent(self.imports)
        if self.body:
            self.body = indent(dedent(self.body), " " * 4)


@dataclass
class ClassOverride:
    base_type: Optional[str] = None
    imports: Optional[str] = None
    fields: Optional[str] = None
    fields_suppress: Set[str] = field(default_factory=set)
    body: Optional[str] = None

    def __post_init__(self) -> None:
        if self.imports:
            self.imports = dedent(self.imports)
        if self.fields:
            self.fields = indent(dedent(self.fields), " " * 4)
        if self.body:
            self.body = indent(dedent(self.body), " " * 4)


# Maps XSD TypeName to Override configuration, used to control output for that type.
OVERRIDES = {
    "MetadataOnly": Override(type_="bool", default="False"),
    # FIXME: Type should be xml.etree.ElementTree.Element but isinstance checks
    # with that class often mysteriously fail so the validator fails.
    "XMLAnnotation/Value": Override(type_="Element"),
    "BinData/Length": Override(type_="int"),
    # FIXME: hard-coded subclass lists
    "Instrument/LightSourceGroup": Override(
        type_="List[LightSource]",
        default="Field(default_factory=list)",
        imports="""
            from typing import Dict, Union, Any
            from pydantic import validator
            from .light_source import LightSource
            from .laser import Laser
            from .arc import Arc
            from .filament import Filament
            from .light_emitting_diode import LightEmittingDiode
            from .generic_excitation_source import GenericExcitationSource

            _light_source_types: Dict[str, type] = {
                "laser": Laser,
                "arc": Arc,
                "filament": Filament,
                "light_emitting_diode": LightEmittingDiode,
                "generic_excitation_source": GenericExcitationSource,
            }
        """,
        body="""
            @validator("light_source_group", pre=True, each_item=True)
            def validate_light_source_group(
                cls, value: Union[LightSource, Dict[Any, Any]]
            ) -> LightSource:
                if isinstance(value, LightSource):
                    return value
                elif isinstance(value, dict):
                    try:
                        _type = value.pop("_type")
                    except KeyError:
                        raise ValueError(
                            "dict initialization requires _type"
                        ) from None
                    try:
                        light_source_cls = _light_source_types[_type]
                    except KeyError:
                        raise ValueError(
                            f"unknown LightSource type '{_type}'"
                        ) from None
                    return light_source_cls(**value)
                else:
                    raise ValueError("invalid type for light_source_group values")
        """,
    ),
    "ROI/Union": Override(
        type_="List[Shape]",
        default="Field(default_factory=list)",
        imports="""
            from typing import Dict, Union, Any
            from pydantic import validator
            from .shape import Shape
            from .point import Point
            from .line import Line
            from .rectangle import Rectangle
            from .ellipse import Ellipse
            from .polyline import Polyline
            from .polygon import Polygon
            from .mask import Mask
            from .label import Label

            _shape_types: Dict[str, type] = {
                "point": Point,
                "line": Line,
                "rectangle": Rectangle,
                "ellipse": Ellipse,
                "polyline": Polyline,
                "polygon": Polygon,
                "mask": Mask,
                "label": Label,
            }
        """,
        body="""
            @validator("union", pre=True, each_item=True)
            def validate_union(
                cls, value: Union[Shape, Dict[Any, Any]]
            ) -> Shape:
                if isinstance(value, Shape):
                    return value
                elif isinstance(value, dict):
                    try:
                        _type = value.pop("_type")
                    except KeyError:
                        raise ValueError(
                            "dict initialization requires _type"
                        ) from None
                    try:
                        shape_cls = _shape_types[_type]
                    except KeyError:
                        raise ValueError(f"unknown Shape type '{_type}'") from None
                    return shape_cls(**value)
                else:
                    raise ValueError("invalid type for union values")
        """,
    ),
    "OME/StructuredAnnotations": Override(
        type_="List[Annotation]",
        default="Field(default_factory=list)",
        imports="""
            from typing import Dict, Union, Any
            from pydantic import validator
            from .annotation import Annotation
            from .boolean_annotation import BooleanAnnotation
            from .comment_annotation import CommentAnnotation
            from .double_annotation import DoubleAnnotation
            from .file_annotation import FileAnnotation
            from .list_annotation import ListAnnotation
            from .long_annotation import LongAnnotation
            from .map_annotation import MapAnnotation
            from .tag_annotation import TagAnnotation
            from .term_annotation import TermAnnotation
            from .timestamp_annotation import TimestampAnnotation
            from .xml_annotation import XMLAnnotation

            _annotation_types: Dict[str, type] = {
                "boolean_annotation": BooleanAnnotation,
                "comment_annotation": CommentAnnotation,
                "double_annotation": DoubleAnnotation,
                "file_annotation": FileAnnotation,
                "list_annotation": ListAnnotation,
                "long_annotation": LongAnnotation,
                "map_annotation": MapAnnotation,
                "tag_annotation": TagAnnotation,
                "term_annotation": TermAnnotation,
                "timestamp_annotation": TimestampAnnotation,
                "xml_annotation": XMLAnnotation,
            }
        """,
        body="""
            @validator("structured_annotations", pre=True, each_item=True)
            def validate_structured_annotations(
                cls, value: Union[Annotation, Dict[Any, Any]]
            ) -> Annotation:
                if isinstance(value, Annotation):
                    return value
                elif isinstance(value, dict):
                    try:
                        _type = value.pop("_type")
                    except KeyError:
                        raise ValueError(
                            "dict initialization requires _type"
                        ) from None
                    try:
                        annotation_cls = _annotation_types[_type]
                    except KeyError:
                        raise ValueError(f"unknown Annotation type '{_type}'") from None
                    return annotation_cls(**value)
                else:
                    raise ValueError("invalid type for annotation values")
        """,
    ),
    "TiffData/UUID": Override(
        type_="Optional[UUID]",
        default="None",
        imports="""
            from typing import Optional
            from .simple_types import UniversallyUniqueIdentifier
            from ome_types._base_type import OMEType

            class UUID(OMEType):
                file_name: str
                value: UniversallyUniqueIdentifier
        """,
    ),
    "M/K": Override(type_="str", default=""),
}


# Maps XSD TypeName to ClassOverride configuration, used to control dataclass
# generation.
CLASS_OVERRIDES = {
    "OME": ClassOverride(
        imports="""
            from typing import Any
            import weakref
            from ome_types import util
            from pathlib import Path
        """,
        body="""
            def __init__(self, **data: Any) -> None:
                super().__init__(**data)
                self._link_refs()

            def _link_refs(self) -> None:
                ids = util.collect_ids(self)
                for ref in util.collect_references(self):
                    ref._ref = weakref.ref(ids[ref.id])

            def __setstate__(self: Any, state: Dict[str, Any]) -> None:
                '''Support unpickle of our weakref references.'''
                super().__setstate__(state)
                self._link_refs()

            @classmethod
            def from_xml(cls, xml: Union[Path, str]) -> 'OME':
                from ome_types._convenience import from_xml
                return from_xml(xml)

            @classmethod
            def from_tiff(cls, path: Union[Path, str]) -> 'OME':
                from ome_types._convenience import from_tiff
                return from_tiff(path)

            def to_xml(self) -> str:
                from ome_types.schema import to_xml
                return to_xml(self)
        """,
    ),
    "Reference": ClassOverride(
        imports="""
            from pydantic import Field
            from typing import Any, Optional, TYPE_CHECKING
            from weakref import ReferenceType
            from .simple_types import LSID
        """,
        fields="""
            if TYPE_CHECKING:
                _ref: Optional["ReferenceType[OMEType]"]

            id: LSID
            _ref = None
        """,
        # FIXME Could make `ref` abstract and implement stronger-typed overrides
        # in subclasses.
        body="""
            @property
            def ref(self) -> Any:
                if self._ref is None:
                    raise ValueError("references not yet resolved on root OME object")
                return self._ref()
        """,
    ),
    "XMLAnnotation": ClassOverride(
        imports="""
            from xml.etree import ElementTree
            from typing import Generator
            from typing import Callable, Generator, Any, Dict

            class Element(ElementTree.Element):
                '''ElementTree.Element that supports pydantic validation.'''
                @classmethod
                def __get_validators__(cls) -> Generator[Callable[[Any], Any], None, None]:
                    yield cls.validate

                @classmethod
                def validate(cls, v: Any) -> ElementTree.Element:
                    if isinstance(v, ElementTree.Element):
                        return v
                    try:
                        return ElementTree.fromstring(v)
                    except ElementTree.ParseError as e:
                        raise ValueError(f"Invalid XML string: {e}")
        """,
        body="""
            # NOTE: pickling this object requires xmlschema>=1.4.1

            def dict(self, **k: Any) -> Dict[str, Any]:
                d = super().dict(**k)
                d["value"] = ElementTree.tostring(
                    d.pop("value"), encoding="unicode", method="xml"
                ).strip()
                return d
        """,
    ),
    "BinData": ClassOverride(base_type="object", fields="value: str"),
    "Map": ClassOverride(fields_suppress={"K"}),
    "M": ClassOverride(base_type="object", fields="value: str"),
}


def autoflake(text: str, **kwargs: Any) -> str:

    kwargs.setdefault("remove_all_unused_imports", True)
    kwargs.setdefault("remove_unused_variables", True)
    return fix_code(text, **kwargs)


def black_format(text: str, line_length: int = 88) -> str:
    return black.format_str(text, mode=black.FileMode(line_length=line_length))


def sort_imports(text: str) -> str:
    return isort.api.sort_code_string(text, profile="black", float_to_top=True)


def sort_types(el: XsdType) -> str:
    if not el.is_complex() and not el.base_type.is_restriction():
        return "    " + el.local_name.lower()
    return el.local_name.lower()


def sort_prop(prop: Member) -> str:
    return ("" if prop.default_val_str else "   ") + prop.format().lower()


def as_identifier(s: str) -> str:
    # Remove invalid characters
    _s = re.sub("[^0-9a-zA-Z_]", "", s)
    # Remove leading characters until we find a letter or underscore
    _s = re.sub("^[^a-zA-Z_]+", "", _s)
    if not _s:
        raise ValueError(f"Could not clean {s}: nothing left")
    return _s


CAMEL_SNAKE_OVERRIDES = {"ROIs": "rois"}


def camel_to_snake(name: str) -> str:
    result = CAMEL_SNAKE_OVERRIDES.get(name, None)
    if not result:
        # https://stackoverflow.com/a/1176023
        result = re.sub("([A-Z]+)([A-Z][a-z]+)", r"\1_\2", name)
        result = re.sub("([a-z0-9])([A-Z])", r"\1_\2", result)
        result = result.lower().replace(" ", "_")
    camel_snake_registry[name] = result
    return result


def local_import(item_type: str) -> str:
    return f"from .{camel_to_snake(item_type)} import {item_type}"


def get_docstring(
    component: Union[XsdComponent, XsdType], summary: bool = False
) -> str:
    try:
        doc = dedent(component.annotation.documentation[0].text).strip()
        # make sure the first line is followed by a double newline
        # and preserve paragraphs
        if summary:
            doc = re.sub(r"\.\s", ".\n\n", doc, count=1)
        # textwrap each paragraph seperately
        paragraphs = ["\n".join(wrap(p.strip(), width=78)) for p in doc.split("\n\n")]
        # join and return
        return "\n\n".join(paragraphs)
    except (AttributeError, IndexError):
        return ""


def make_dataclass(component: Union[XsdComponent, XsdType]) -> List[str]:
    class_override = CLASS_OVERRIDES.get(component.local_name, None)
    lines = ["from ome_types._base_type import OMEType", ""]
    if isinstance(component, XsdType):
        base_type = component.base_type
    else:
        base_type = component.type.base_type

    if class_override and class_override.base_type:
        if class_override.base_type == "object":
            base_name = "(OMEType)"
        else:
            base_name = f"({class_override.base_type}, OMEType)"
        base_type = None
    elif base_type and not hasattr(base_type, "python_type"):
        base_name = f"({base_type.local_name}, OMEType)"
        if base_type.is_complex():
            lines += [local_import(base_type.local_name)]
        else:
            lines += [f"from .simple_types import {base_type.local_name}"]
    else:
        base_name = "(OMEType)"
    if class_override and class_override.imports:
        lines.append(class_override.imports)

    base_members = set()
    _basebase = base_type
    while _basebase:
        base_members.update(set(iter_members(base_type)))
        _basebase = _basebase.base_type
    skip_names = set()
    if class_override:
        skip_names.update(class_override.fields_suppress)

    members = MemberSet(
        m
        for m in iter_members(component)
        if m not in base_members and m.local_name not in skip_names
    )
    lines += members.imports()
    lines += members.locals()

    lines += [f"class {component.local_name}{base_name}:"]
    doc = get_docstring(component, summary=True)
    doc = MemberSet(iter_members(component)).docstring(
        doc or f"{component.local_name}."
    )
    doc = f'"""{doc.strip()}\n"""\n'
    lines += indent(doc, "    ").splitlines()
    if class_override and class_override.fields:
        lines.append(class_override.fields)
    lines += members.lines(indent=1)

    if class_override and class_override.body:
        lines.append(class_override.body)
    lines += members.body()

    return lines


def make_enum(component: XsdComponent) -> List[str]:
    name = component.local_name
    _type = component.type if hasattr(component, "type") else component
    if _type.is_list():
        _type = _type.item_type
    lines = ["from enum import Enum", ""]
    lines += [f"class {name}(Enum):"]
    doc = get_docstring(component, summary=True)
    if doc:
        if not doc.endswith("."):
            doc += "."
        doc = f'"""{doc}\n"""\n'
        lines += indent(doc, "    ").splitlines()
    enum_elems = list(_type.elem.iter("enum"))
    facets = _type.get_facet(qnames.XSD_ENUMERATION)
    members: List[Tuple[str, str]] = []
    if enum_elems:
        for el, value in zip(enum_elems, facets.enumeration):
            _name = el.attrib["enum"]
            if _type.base_type.python_type.__name__ == "str":
                value = f'"{value}"'
            members.append((_name, value))
    else:
        for e in facets.enumeration:
            members.append((camel_to_snake(e), repr(e)))

    for n, v in sorted(members):
        lines.append(f"    {as_identifier(n).upper()} = {v}")
    return lines


def make_color() -> List[str]:
    color = """
    from pydantic import color
    class Color(color.Color):
        def __init__(self, val: color.ColorType) -> None:
            if isinstance(val, int):
                val = self._int2tuple(val)
            super().__init__(val)

        @classmethod
        def _int2tuple(cls, val: int):
            return (val >> 24 & 255, val >> 16 & 255, val >> 8 & 255, (val & 255) / 255)

        def as_int32(self) -> int:
            r, g, b, *a = self.as_rgb_tuple()
            v = r << 24 | g << 16 | b << 8 | int((a[0] if a else 1) * 255)
            if v < 2 ** 32 // 2:
                return v
            return v - 2 ** 32

        def __eq__(self, o: object) -> bool:
            if isinstance(o, Color):
                return self.as_int32() == o.as_int32()
            return False

        def __int__(self) -> int:
            return self.as_int32()
    """
    return dedent(color).strip().splitlines()


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


def iter_all_members(
    component: XsdComponent,
) -> Generator[Union[XsdElement, XsdAttribute], None, None]:
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


def is_enum_type(obj: XsdType) -> bool:
    """Return true if XsdType represents an enumeration."""
    return obj.get_facet(qnames.XSD_ENUMERATION) is not None


class Member:
    def __init__(self, component: Union[XsdElement, XsdAttribute]):
        self.component = component
        assert not component.is_global()

    @property
    def identifier(self) -> str:
        if isinstance(self.component, (XsdAnyElement, XsdAnyAttribute)):
            return self.component.local_name
        name = camel_to_snake(self.component.local_name)
        if self.plural:
            plural = camel_to_snake(self.plural)
            plural_registry[(self.parent_name, name)] = plural
            name = plural
        if not name.isidentifier():
            raise ValueError(f"failed to make identifier of {self!r}")
        return name

    @property
    def plural(self) -> Optional[str]:
        """Plural form of component name, if available."""
        if (
            isinstance(self.component, XsdElement)
            and self.component.is_multiple()
            and self.component.ref
            and self.component.ref.annotation
        ):
            appinfo = self.component.ref.annotation.appinfo
            assert len(appinfo) == 1, "unexpected multiple appinfo elements"
            plural = appinfo[0].find("xsdfu/plural")
            if plural is not None:
                return plural.text
        return None

    @property
    def type(self) -> XsdType:
        return self.component.type

    def to_numpydoc_param(self) -> Parameter:
        _type = self.type_string
        _type += ", optional" if self.is_optional else ""
        desc = get_docstring(self.component)
        desc = re.sub(r"\s?\[.+\]", "", desc)  # remove bracketed types
        return Parameter(self.identifier, _type, wrap(desc))

    @property
    def is_builtin_type(self) -> bool:
        return hasattr(self.type, "python_type")

    @property
    def is_decimal(self) -> bool:
        return self.component.type.is_derived(
            self.component.schema.builtin_types()["decimal"]
        )

    @property
    def is_nonref_id(self) -> bool:
        """Return True for 'id' fields that aren't part of a Reference type."""
        if self.identifier != "id":
            return False
        # Walk up the containment tree until we find something with a base_type.
        p = self.component.parent
        while p is not None and not hasattr(p, "base_type"):
            p = p.parent
        if p is not None:
            # Walk the type hierarchy looking for 'Reference'.
            pt = p.base_type
            while pt is not None:
                if pt.local_name == "Reference":
                    return False
                pt = pt.base_type
        # If we get here, we have an 'id' that isn't in a Reference type.
        return True

    @property
    def is_ref_id(self) -> bool:
        if self.identifier == "id":
            return not self.is_nonref_id
        return False

    @property
    def parent_name(self) -> str:
        """Local name of component's first named ancestor."""
        p = self.component.parent
        while not p.local_name and p.parent is not None:
            p = p.parent
        return p.local_name

    @property
    def key(self) -> str:
        name = f"{self.parent_name}/{self.component.local_name}"
        if name not in OVERRIDES and self.component.local_name in OVERRIDES:
            return self.component.local_name
        return name

    def locals(self) -> List[str]:
        if self.key in OVERRIDES:
            return []
        if isinstance(self.component, (XsdAnyElement, XsdAnyAttribute)):
            return []
        if not self.type or self.type.is_global():
            return []
        locals_: List[str] = []
        # FIXME: this bit is mostly hacks
        if self.type.is_complex() and self.component.ref is None:
            locals_.append("\n".join(make_dataclass(self.component)) + "\n")
        if self.type.is_restriction() and is_enum_type(self.type):
            locals_.append("\n".join(make_enum(self.component)) + "\n")
        if self.type.is_list() and is_enum_type(self.type.item_type):
            locals_.append("\n".join(make_enum(self.component)) + "\n")
        return locals_

    def imports(self) -> List[str]:
        if self.key in OVERRIDES:
            _imp = OVERRIDES[self.key].imports
            return [_imp] if _imp else []
        if isinstance(self.component, (XsdAnyElement, XsdAnyAttribute)):
            return ["from typing import Any"]
        imports = []
        if not self.max_occurs:
            imports.append("from typing import List")
            if self.is_optional:
                imports.append("from pydantic import Field")
        elif self.is_optional:
            imports.append("from typing import Optional")
        if self.is_decimal:
            imports.append("from typing import cast")
        if self.type.is_datetime():
            imports.append("from datetime import datetime")
        if not self.is_builtin_type and self.type.is_global():
            # FIXME: hack
            if not self.type.local_name == "anyType":
                if self.type.is_complex():
                    imports.append(local_import(self.type.local_name))
                else:
                    imports.append(f"from .simple_types import {self.type.local_name}")

        if self.component.ref is not None:
            if self.component.ref.local_name not in OVERRIDES:
                imports.append(local_import(self.component.ref.local_name))

        return imports

    def body(self) -> str:
        if self.key in OVERRIDES:
            return OVERRIDES[self.key].body or ""
        return ""

    @property
    def type_string(self) -> str:
        """single type, without Optional, etc..."""
        if self.key in OVERRIDES:
            return OVERRIDES[self.key].type_
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
        elif self.type.is_complex() or self.type.is_list():
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
        if self.key in OVERRIDES and self.type_string:
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
        if self.key in OVERRIDES:
            default = OVERRIDES[self.key].default
            return f" = {default}" if default else ""
        elif not self.is_optional:
            return ""

        if not self.max_occurs:
            default_val = "Field(default_factory=list)"
        else:
            default_val = self.component.default
            if default_val is not None:
                if is_enum_type(self.type):
                    default_val = f"{self.type_string}('{default_val}')"
                elif hasattr(builtins, self.type_string):
                    default_val = repr(getattr(builtins, self.type_string)(default_val))
                if self.is_decimal:
                    default_val = f"cast({self.type_string}, {default_val})"
            else:
                default_val = "None"
        return f" = {default_val}"

    @property
    def max_occurs(self) -> bool:
        default = None if self.type.is_list() else 1
        return getattr(self.component, "max_occurs", default)

    @property
    def is_optional(self) -> bool:
        if self.is_ref_id:
            return False
        if getattr(self.component.parent, "model", "") == "choice":
            return True
        if hasattr(self.component, "min_occurs"):
            return self.component.min_occurs == 0
        return self.component.is_optional()

    def __repr__(self) -> str:
        type_ = "element" if isinstance(self.component, XsdElement) else "attribute"
        return f"<Member {type_} {self.component.local_name}>"

    def format(self) -> str:
        return f"{self.identifier}{self.full_type_string}{self.default_val_str}"


class MemberSet:
    def __init__(self, initial: Iterable[Member] = ()):
        # Use a list to maintain insertion order.
        self._members: List[Member] = []
        self.update(initial)

    def add(self, member: Member) -> None:
        if not isinstance(member, Member):
            member = Member(member)
        # We don't expect very many elements so this O(n) check is fine.
        if member in self._members:
            return
        self._members.append(member)

    def update(self, members: Iterable[Member]) -> None:
        for member in members:
            self.add(member)

    def lines(self, indent: int = 1) -> List[str]:
        if not self._members:
            lines = ["    " * indent + "pass"]
        else:
            lines = [
                "    " * indent + m.format()
                for m in sorted(self._members, key=sort_prop)
            ]
        return lines

    def imports(self) -> List[str]:
        return list(chain.from_iterable(m.imports() for m in self._members))

    def locals(self) -> List[str]:
        return list(chain.from_iterable(m.locals() for m in self._members))

    def body(self) -> List[str]:
        return [m.body() for m in self._members]

    def has_non_default_args(self) -> bool:
        return any(not m.default_val_str for m in self._members)

    def has_nonref_id(self) -> bool:
        return any(m.is_nonref_id for m in self._members)

    @property
    def non_defaults(self) -> "MemberSet":
        return MemberSet(m for m in self._members if not m.default_val_str)

    def __iter__(self) -> Iterator[Member]:
        return iter(self._members)

    def docstring(self, summary: str = "") -> str:
        ds = NumpyDocString(summary)
        ds["Parameters"] = [
            m.to_numpydoc_param() for m in sorted(self._members, key=sort_prop)
        ]
        return str(ds)


class GlobalElem:
    def __init__(self, elem: Union[XsdElement, XsdType]):
        assert elem.is_global()
        self.elem = elem

    @property
    def type(self) -> XsdType:
        return self.elem if self.is_type else self.elem.type

    @property
    def is_complex(self) -> bool:
        if hasattr(self.type, "is_complex"):
            return self.type.is_complex()
        return False

    @property
    def is_element(self) -> bool:
        return isinstance(self.elem, XsdElement)

    @property
    def is_type(self) -> bool:
        return isinstance(self.elem, XsdType)

    @property
    def is_enum(self) -> bool:
        is_enum = bool(self.elem.get_facet(qnames.XSD_ENUMERATION) is not None)
        if is_enum:
            if not len(self.elem.facets) == 1:
                raise NotImplementedError("Unexpected enum with multiple facets")
        return is_enum

    def _simple_class(self) -> List[str]:
        if self.type.local_name == "Color":
            return make_color()
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
        return black_format(sort_imports(autoflake(self.lines() + "\n")))

    def write(self, filename: str) -> None:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.format())

    @property
    def fname(self) -> str:
        return f"{camel_to_snake(self.elem.local_name)}.py"


_this_dir = os.path.dirname(__file__)
_url = os.path.join(_this_dir, "ome_types", "ome-2016-06.xsd")
_target = os.path.join(_this_dir, "ome_types", "model")


def convert_schema(url: str = _url, target_dir: str = _target) -> None:
    print("Inspecting XML schema ...")
    if isinstance(url, Path):
        url = str(url)
    schema = XMLSchema(url)
    print("Building model ...")
    shutil.rmtree(target_dir, ignore_errors=True)
    init_imports = []
    simples: List[GlobalElem] = []
    for elem in sorted(schema.types.values(), key=sort_types):
        if elem.local_name in OVERRIDES:
            continue
        converter = GlobalElem(elem)
        if not elem.is_complex():
            simples.append(converter)
            continue
        targetfile = os.path.join(target_dir, converter.fname)
        init_imports.append((converter.fname, elem.local_name))
        converter.write(filename=targetfile)

    for elem in schema.elements.values():
        if elem.local_name in OVERRIDES:
            continue
        converter = GlobalElem(elem)
        targetfile = os.path.join(target_dir, converter.fname)
        init_imports.append((converter.fname, elem.local_name))
        converter.write(filename=targetfile)

    text = "\n".join([s.format() for s in simples])
    text = black_format(sort_imports(text))
    with open(os.path.join(target_dir, "simple_types.py"), "w", encoding="utf-8") as f:
        f.write(text)

    text = ""
    for fname, classname in init_imports:
        text += local_import(classname) + "\n"
    text = sort_imports(text)
    text += f"\n\n__all__ = [{', '.join(sorted(repr(i[1]) for i in init_imports))}]"
    # FIXME These could probably live somewhere else less visible to end-users.
    if len(plural_registry) != len(set(plural_registry.values())):
        raise Exception(
            "singular-to-plural mapping is not invertible (duplicate plurals)"
        )
    text += "\n\n_singular_to_plural = " + repr(
        {k: plural_registry[k] for k in sorted(plural_registry)}
    )
    text += "\n\n_plural_to_singular = " + repr(
        {plural_registry[k]: k[1] for k in sorted(plural_registry)}
    )
    if len(camel_snake_registry) != len(set(camel_snake_registry.values())):
        raise Exception("camel-to-snake mapping is not invertible (duplicate snakes)")
    text += "\n\n_camel_to_snake = " + repr(
        {k: camel_snake_registry[k] for k in sorted(camel_snake_registry)}
    )
    text += "\n\n_snake_to_camel = " + repr(
        {camel_snake_registry[k]: k for k in sorted(camel_snake_registry)}
    )
    text = black_format(text)
    with open(os.path.join(target_dir, "__init__.py"), "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    # for testing
    convert_schema()
