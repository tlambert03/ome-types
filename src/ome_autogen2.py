"""Logic to parse an OME XSD file and generate a Python class for each type.

TOP level elements in OME.xsd
['annotation', 'complexType', 'element', 'import', 'simpleType']

ALL elements seen in the entire OME.xsd
[
 'abstract', 'annotation', 'any', 'appinfo', 'attribute', 'childordered',
 'choice', 'complexContent', 'complexType', 'documentation', 'element', 'enum',
 'enumeration', 'extension', 'field', 'global', 'import', 'injected', 'key',
 'keyref', 'length', 'list', 'manytomany', 'maxInclusive', 'minExclusive',
 'minInclusive', 'ordered', 'parentordered', 'pattern', 'plural', 'restriction',
 'selector', 'sequence', 'simpleContent', 'simpleType', 'unique',
 'whiteSpace', 'xsdfu'
]

"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field, fields
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Iterator, Union, overload

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree  # type: ignore

if TYPE_CHECKING:
    from typing import Any, Literal, TypeVar

    from lxml.etree import _Element as EtreeElement

    T = TypeVar("T")


XSD_NS = "http://www.w3.org/2001/XMLSchema"
OME_NS = "http://www.openmicroscopy.org/Schemas/OME/2016-06"

QName = etree.QName
XSD_SCHEMA = QName(XSD_NS, "schema").text
XSD_ANNOTATION = QName(XSD_NS, "annotation").text
XSD_COMPLEX_TYPE = QName(XSD_NS, "complexType").text
XSD_ELEMENT = QName(XSD_NS, "element").text
XSD_IMPORT = QName(XSD_NS, "import").text
XSD_SIMPLE_TYPE = QName(XSD_NS, "simpleType").text

XSD_KEY = QName(XSD_NS, "key").text  # appear in root OME element, or Plate element
XSD_KEYREF = QName(XSD_NS, "keyref").text  # only appear in root OME element
XSD_ATTRIBUTE = QName(XSD_NS, "attribute").text  # appear in complexType or extension
XSD_DOCUMENTATION = QName(XSD_NS, "documentation").text  # only appear in annotation
XSD_APPINFO = QName(XSD_NS, "appinfo").text  # only appear in annotation
XSD_SEQUENCE = QName(XSD_NS, "sequence").text  # in complexType, choice, extension, seq
XSD_CHOICE = QName(XSD_NS, "choice").text  # appear in complexType or sequences
XSD_RESTRICTION = QName(XSD_NS, "restriction").text  # only appear in simpleType
XSD_EXTENSION = QName(XSD_NS, "extension").text  # appear in [simple|complex]Content
XSD_LIST = QName(XSD_NS, "list").text  # only appear in simpleType
XSD_ANY = QName(XSD_NS, "any").text  # only appear in sequence
XSD_ENUMERATION = QName(XSD_NS, "enumeration").text  # only appear in restriction

XSD_COMMENT = etree.Comment
_XSDFU = QName(None, "xsdfu").text  # always in appinfo
_PLURAL = QName(None, "plural").text  # always in xsdfu

_PARENT_MAP: dict[EtreeElement, EtreeElement] = {}
FLAT_NAMES = {}


# ############### Helper functions #################

# not used yet...
XSD_TYPES = {
    "xsd:anyURI": str,
    "xsd:boolean": int,
    "xsd:dateTime": datetime.datetime,
    "xsd:double": float,
    "xsd:float": float,
    "xsd:int": int,
    "xsd:long": int,
    "xsd:string": str,
}


def _iter_non_null_fields(obj: object) -> Iterator[tuple[str, Any]]:
    for f in fields(obj):
        if f.repr and (value := getattr(obj, f.name)) not in (None, []):
            yield f.name, value


def __non_null_repr__(self: object) -> str:
    non_none_fields = [f"{name}={val!r}" for name, val in _iter_non_null_fields(self)]
    return f"{self.__class__.__name__}({', '.join(non_none_fields)})"


def _min_max_occurs(node: EtreeElement) -> tuple[int | None, int | None]:
    # if minOccurs is defined, maxOccurs will either be an int or 'unbounded'

    _min = node.attrib.get("minOccurs")
    _max = node.attrib.get("maxOccurs")
    min_occurs = int(_min) if _min else None
    max_occurs = int(_max) if _max and _max != "unbounded" else None
    return (min_occurs, max_occurs)


def _get_value(node: EtreeElement, value: str | QName, type_: type[T]) -> T | None:
    if isinstance(value, str):
        value = QName(XSD_NS, value)
    if (elem := node.find(value)) is not None:
        return type_(elem.attrib["value"])
    return None


def _get_enums(node: EtreeElement) -> list[str]:
    return [e.attrib["value"] for e in node.findall(XSD_ENUMERATION)]  # type: ignore


# ############### Dataclasses for the parsed XSD #################


@dataclass
class ParsedNode:
    _node: EtreeElement = field(repr=False)

    __rich_repr__ = _iter_non_null_fields

    @property
    def parent(self) -> Element | None:
        return _PARENT_MAP.get(self._node)


@dataclass
class Element(ParsedNode):
    """An xsd:element in the schema."""

    # either name or ref must be set
    name: str | None = None
    ref: str | None = None

    type: str | None = None
    annotation: Annotation | None = None
    min_occurs: int | None = None
    max_occurs: int | None = None
    substitution_group: str | None = None
    complex_type: ComplexType | None = None
    simple_type: SimpleType | None = None
    keys: list[EtreeElement] = field(default_factory=list)
    keyrefs: list[EtreeElement] = field(default_factory=list)
    is_abstract: bool = False

    def __post_init__(self) -> None:
        if self.name is None and self.ref is None:
            raise ValueError("Element must have name or ref")


@dataclass
class ComplexType(ParsedNode):
    """An xsd:complexType in the schema."""

    name: str | None = None
    annotation: Annotation | None = None
    attributes: list[Attribute] = field(default_factory=list)
    sequence: Any = None
    choice: Choice | None = None


@dataclass
class SimpleType(ParsedNode):
    """An xsd:simpleType in the schema."""

    name: str | None = None
    annotation: Annotation | None = None
    restriction: Restriction | None = None
    list: list[str] = field(default_factory=list)


@dataclass
class Sequence(ParsedNode):
    elements: list[Element] = field(default_factory=list)
    choice: Choice | None = None
    any: EtreeElement | None = None
    sequence: Sequence | None = None
    min_occurs: int | None = None
    max_occurs: int | None = None


@dataclass
class Annotation(ParsedNode):
    appinfo: EtreeElement | None = None
    documentation: Documentation | None = None


@dataclass
class Attribute(ParsedNode):
    name: str
    type: str | None = None
    use: Literal["optional", "required"] | None = None
    default: str | None = None
    annotation: Annotation | None = None
    simple_type: SimpleType | None = None


@dataclass
class Documentation(ParsedNode):
    text: str

    def __str__(self) -> str:
        return dedent(self.text).strip()

    def __rich_repr__(self) -> Iterator[tuple[str, str]]:  # type: ignore
        yield "text", str(self)


@dataclass
class Choice(ParsedNode):
    annotation: Annotation | None = None
    sequence: Sequence | None = None
    elements: list[Element] = field(default_factory=list)
    min_occurs: int | None = None
    max_occurs: int | None = None  # None means unbounded


@dataclass
class Restriction(ParsedNode):
    base: str
    enums: list[str] = field(default_factory=list)
    length: int | None = None
    min_inclusive: float | None = None
    min_exclusive: float | None = None
    max_inclusive: float | None = None
    pattern: str | None = None
    whitespace: Literal["collapse", "preserve", "replace"] | None = None

    __repr__ = __non_null_repr__


# ############### visitor functions #################

# fmt: off
@overload
def _visit(node: EtreeElement, qname: Literal["annotation"]) -> Annotation | None: ...
@overload
def _visit(node: EtreeElement, qname: Literal["complexType"]) -> ComplexType | None: ...
@overload
def _visit(node: EtreeElement, qname: Literal["simpleType"]) -> SimpleType | None: ...
@overload
def _visit(node: EtreeElement, qname: Literal["sequence"]) -> Sequence | None: ...
@overload
def _visit(node: EtreeElement, qname: Literal["choice"]) -> Choice | None: ...
@overload
def _visit(node: EtreeElement, qname: Literal["documentation"]) -> Documentation | None: ...
@overload
def _visit(node: EtreeElement, qname: Literal["restriction"]) -> Restriction: ...
@overload
def _visit(node: EtreeElement, qname: Literal["list"]) -> list[str]: ...
@overload
def _visit(node: EtreeElement, qname: QName) -> Any | None: ...
def _visit(node: EtreeElement, qname: QName | str) -> Any | None:
    if isinstance(qname, str):
        qname = QName(XSD_NS, qname)
    # sourcery skip: reintroduce-else
    if (child := node.find(str(qname))) is not None:
        return visit_node(child)
    return None

@overload
def _visitall(node: EtreeElement, qname: Literal["attribute"]) -> list[Attribute]: ...
@overload
def _visitall(node: EtreeElement, qname: Literal["element"]) -> list[Element]: ...
@overload
def _visitall(node: EtreeElement, qname: QName) -> list[Any]: ...
def _visitall(node: EtreeElement, qname: QName | str) -> list[Any]:
    if isinstance(qname, str):
        qname = QName(XSD_NS, qname)
    return [visit_node(child) for child in node.findall(str(qname))]
# fmt: on


def visit_element(elem: EtreeElement) -> Element:
    min_occ, max_occ = _min_max_occurs(elem)
    return Element(
        _node=elem,
        # in OME, all elements have either a name XOR a ref
        # (if it is abstract or has a substitutionGroup, it will never have a ref)
        name=elem.attrib.get("name"),
        ref=elem.attrib.get("ref"),
        # a few _named elements will have a _type, but most will not
        # if present, it will be one of:
        # 'AffineTransform', 'FilterRef', 'Hex40', 'LightSource', 'Map', 'Shape',
        # 'xsd:boolean', 'xsd:dateTime', 'xsd:double', 'xsd:long', 'xsd:string'
        type=elem.attrib.get("type"),
        # - 0 or 1 'annotation' elements
        annotation=_visit(elem, "annotation"),
        # minOccurs and maxOccurs will only be present if this element is a child
        # of either a 'sequence' or 'choice' element
        min_occurs=min_occ,
        max_occurs=max_occ,
        # for OME, this is only ever ShapeGroup or LightSourceGroup
        substitution_group=elem.attrib.get("substitutionGroup"),
        # if it is a named element (but not a _ref), it may additionally have
        #   - 0-1 'complexType' element OR 0-1 'simpleType' element (but not both)
        # note that none of the top level elements in OME have a simpleType
        # they only ever appear in elements that are children of a sequence
        # always a "Description", "RightsHolder", or "RightsHeld" element
        complex_type=_visit(elem, "complexType"),
        simple_type=_visit(elem, "simpleType"),
        #   - zero or more 'key' elements
        keys=elem.findall(XSD_KEY),
        #   - zero or more 'keyref' elements (only in the root OME type)
        keyrefs=elem.findall(XSD_KEYREF),
        is_abstract=elem.attrib.get("abstract") in ("true", "1"),
    )


def visit_attribute(attrib: EtreeElement) -> Attribute:
    return Attribute(
        _node=attrib,
        name=attrib.attrib["name"],  # all attributes in OME have a name
        type=attrib.attrib.get("type"),
        use=attrib.attrib.get("use"),  # type: ignore
        default=attrib.attrib.get("default"),
        #  - 0 or 1 'annotation' elements
        annotation=_visit(attrib, "annotation"),
        #  - 0 or 1 'simpleType' elements
        simple_type=_visit(attrib, "simpleType"),
    )


def visit_complexType(complex_type: EtreeElement) -> ComplexType:
    return ComplexType(
        _node=complex_type,
        name=complex_type.attrib.get("name"),  # might be None
        annotation=_visit(complex_type, "annotation"),  # 0 or 1
        attributes=_visitall(complex_type, "attribute"),  # 0 or more
        sequence=_visit(complex_type, "sequence"),  # 0 or 1
        choice=_visit(complex_type, "choice"),  # 0 or 1
        # TODO:
        # - 0 or 1 'simpleContent' elements ...
        # - 0 or 1 'complexContent' elements ...
    )


def visit_simpleType(simple_type: EtreeElement) -> SimpleType:
    return SimpleType(
        _node=simple_type,
        name=simple_type.attrib.get("name"),  # might be None
        annotation=_visit(simple_type, "annotation"),  # 0 or 1
        restriction=_visit(simple_type, "restriction"),  # 0 or 1
        list=_visit(simple_type, "list"),  # 0 or 1
    )


def visit_annotation(annot: EtreeElement) -> Annotation:
    return Annotation(
        _node=annot,
        # if present, an appinfo always contains one 'xsdfu' element
        # xsdfu can contain plural/manytomany/ordered/unique/global/abstract/injected
        appinfo=annot.find(XSD_APPINFO),  # 0 or 1
        documentation=_visit(annot, "documentation"),  # 0 or 1
    )


def visit_sequence(seq: EtreeElement) -> Sequence:
    return Sequence(
        _node=seq,
        elements=_visitall(seq, "element"),  # 0 or more
        choice=_visit(seq, "choice"),  # 0 or 1
        any=seq.find(XSD_ANY),  # 0 or 1
        sequence=_visit(seq, "sequence"),  # 0 or 1
        min_occurs=int(x) if (x := seq.attrib.get("minOccurs")) else None,
        max_occurs=int(x) if (x := seq.attrib.get("maxOccurs")) else None,
    )


def visit_list(lst: EtreeElement) -> list[str]:
    # The only two <xsd:list> elements in OME are inside of Experiment and MicroBeam...
    # they each have a single <xsd:simpleType> child
    # which has a single <xsd:restriction base="xsd:string"> child
    # This probably doesn't generalize outside of OME, so we'll just hardcode it
    # and raise an error if we see anything else
    if (
        ((simple_type := lst.find(XSD_SIMPLE_TYPE)) is None)
        or ((restriction := simple_type.find(XSD_RESTRICTION)) is None)
        or (restriction.attrib["base"] != "xsd:string")
    ):
        raise ValueError(
            "Expected OME <xsd:list> to have a single <xsd:simpleType> child "
            "with a single <xsd:restriction base='xsd:string'> child."
        )

    return _get_enums(restriction)


def visit_choice(choice: EtreeElement) -> Choice:
    min_occ, max_occ = _min_max_occurs(choice)
    return Choice(
        _node=choice,
        annotation=_visit(choice, "annotation"),  # 0 or 1
        min_occurs=min_occ,
        max_occurs=max_occ,
        sequence=_visit(choice, "sequence"),  # 0 or 1
        elements=_visitall(choice, "element"),  # 0 or more
    )


def visit_documentation(doc: EtreeElement) -> Documentation:
    return Documentation(_node=doc, text=doc.text or "")


def visit_restriction(restr: EtreeElement) -> Restriction:
    # pattern (0 or 1)
    # whiteSpace (0 or 1)
    return Restriction(
        _node=restr,
        base=restr.attrib["base"],
        enums=_get_enums(restr),  # (0 or more... and only if base=xsd:string)
        length=_get_value(restr, "length", int),  # only in base=xsd:hexBinary
        min_inclusive=_get_value(restr, "minInclusive", float),  # only when base=number
        min_exclusive=_get_value(restr, "minExclusive", float),  # only when base=float
        max_inclusive=_get_value(restr, "maxInclusive", float),  # only when base=float
        pattern=_get_value(restr, "pattern", str),
        whitespace=_get_value(restr, "whiteSpace", str),  # type: ignore [arg-type]
    )


ParsedItem = Union[
    Sequence,
    SimpleType,
    ComplexType,
    Annotation,
    Restriction,
    Attribute,
    Element,
    Documentation,
    Choice,
    list[str],
]


def visit_node(node: EtreeElement) -> ParsedItem | None:
    if node.tag in (etree.Comment, XSD_IMPORT, XSD_SCHEMA):
        return None

    # get the appropriate visit function based on the node name
    func_name = f"visit_{QName(node).localname}"
    if func_name not in globals():
        raise NotImplementedError(f"a {func_name!r} function has not been implemented")

    # visit the node
    parsed = globals()[func_name](node)

    # add to the global namespace
    if (name := getattr(parsed, "name", None)) and not isinstance(parsed, Attribute):
        # if name in FLAT_NAMES:
        #     warnings.warn(f"Duplicate global name: {name!r}", stacklevel=1)
        FLAT_NAMES[name] = parsed

    return parsed


# #################### MAIN ####################


def main(fpath: Path | str) -> list[ParsedItem]:
    """Return a list of top-level parsed items from the given XSD file."""
    root = etree.XML(Path(fpath).read_bytes())

    # not needed, but useful for debugging
    for p in etree.ElementTree(root).iter():
        for c in p:
            _PARENT_MAP[c] = p

    # at the top level, these will only be elements, complexTypes, and simpleTypes
    # (and one annotation and import, which we can ignore)
    return [x for item in root if (x := visit_node(item)) is not None]


if __name__ == "__main__":
    SRC = Path(__file__).parent
    TOP = main(SRC / "ome_types" / "ome-2016-06.xsd")
    NAMES = {x.name: x for x in TOP if hasattr(x, "name")}
