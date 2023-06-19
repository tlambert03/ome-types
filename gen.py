import datetime
from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree
from rich import inspect as i  # noqa
from rich import print

XSD = "http://www.w3.org/2001/XMLSchema"
# TOP level elements:
# ['annotation', 'complexType', 'element', 'import', 'simpleType']
XSD_ANNOTATION = etree.QName(XSD, "annotation")
XSD_COMPLEX_TYPE = etree.QName(XSD, "complexType")
XSD_ELEMENT = etree.QName(XSD, "element")
XSD_IMPORT = etree.QName(XSD, "import")
XSD_SIMPLE_TYPE = etree.QName(XSD, "simpleType")

XSD_KEY = etree.QName(XSD, "key")
XSD_KEYREF = etree.QName(XSD, "keyref")
XSD_ATTRIBUTE = etree.QName(XSD, "attribute")

# ALL elements in the entire tree
# [
#  'abstract', 'annotation', 'any', 'appinfo', 'attribute', 'childordered',
#  'choice', 'complexContent', 'complexType', 'documentation', 'element', 'enum',
#  'enumeration', 'extension', 'field', 'global', 'import', 'injected', 'key',
#  'keyref', 'length', 'list', 'manytomany', 'maxInclusive', 'minExclusive',
#  'minInclusive', 'ordered', 'parentordered', 'pattern', 'plural', 'restriction',
#  'selector', 'sequence', 'simpleContent', 'simpleType', 'unique',
#  'whiteSpace', 'xsdfu'
# ]

# These may be seen somewhere inside of an element tag
# [            'annotation', 'any', 'appinfo', 'attribute', 'childordered',
#   'choice', 'complexContent', 'complexType', 'documentation', 'element',
#   'enumeration', 'extension', 'field', 'global',          'injected', 'key',
#   'keyref',          'list', 'manytomany',
#                  'ordered', 'parentordered',            'plural', 'restriction',
#   'selector', 'sequence', 'simpleContent', 'simpleType', 'unique',
#   'whiteSpace', 'xsdfu'
# ]


SCHEMA = Path(__file__).parent / "src" / "ome_types" / "ome-2016-06.xsd"


tree = etree.parse(SCHEMA)  # noqa: S320
# schema = etree.XMLSchema(tree)
root = etree.XML(SCHEMA.read_bytes())


XSD_TYPES = {
    "xsd:boolean": int,
    "xsd:dateTime": datetime.datetime,
    "xsd:double": float,
    "xsd:long": int,
    "xsd:string": str,
}


@dataclass
class Element:
    """An xsd:element in the schema."""

    name: str | None = None
    ref: str | None = None
    type: str | None = None
    min_occurs: int | None = None
    max_occurs: int | None = None
    is_abstract: bool = False
    substitution_group: str | None = None
    children: list = field(default_factory=list)


def visit_element(elem: etree._Element) -> None:
    # in OME, all elements have either a name XOR a ref
    print("       visit_element", elem.attrib)
    _name = elem.attrib.get("name")
    _ref = elem.attrib.get("ref")

    # a few _named elements will have a _type, but most will not
    # if present, it will be one of:
    # 'AffineTransform', 'FilterRef', 'Hex40', 'LightSource', 'Map', 'Shape',
    # 'xsd:boolean', 'xsd:dateTime', 'xsd:double', 'xsd:long', 'xsd:string'
    _type = elem.attrib.get("type")
    _min = elem.attrib.get("minOccurs")  # int | None
    _max = elem.attrib.get("maxOccurs")  # int | None | Literal["unbounded"]
    # (and note that if _min is defined, _max will either be an int or 'unbounded')

    _is_abstract = elem.attrib.get("abstract") in ("true", "1")
    # for OME, this is only ever ShapeGroup or LightSourceGroup
    _substitution_group = elem.attrib.get("substitutionGroup")
    # (if is abstract or has a substitutionGroup, it will never have a _ref)

    # if it is a _ref, it will have
    #   - zero or 1 annotation
    # if it has a _name, then it will have
    #   - zero or 1 annotation
    #   - zero or more 'key' elements
    #   - zero or more 'keyref' elements (only in the root OME type)
    #   - 0-1 'complexType' element OR 0-1 'simpleType' element
    elem.find(XSD_ANNOTATION)
    complex_type = elem.find(XSD_COMPLEX_TYPE)
    elem.find(XSD_SIMPLE_TYPE)
    elem.findall(XSD_KEY)
    elem.findall(XSD_KEYREF)
    if complex_type is not None:
        complex_type.getchildren()
        breakpoint()


def visit_attribute(attrib: etree._Element) -> None:
    print("       visit_attrib", attrib.attrib)


def visit_node(node: etree._Element) -> None:
    if node.tag is etree.Comment:
        return
    qname = etree.QName(node)
    if qname == XSD_ELEMENT:
        visit_element(node)
    elif qname == XSD_ATTRIBUTE:
        visit_attribute(node)
    elif qname == XSD_IMPORT:
        return
    elif qname == XSD_ANNOTATION:
        return


for item in root:
    if item.tag is not etree.Comment:
        print(">>", item.tag, item.attrib)
        visit_node(item)
