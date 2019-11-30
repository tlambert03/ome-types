import os

import xmlschema


XSD = os.path.join(os.path.dirname(__file__), "ome.xsd")
schema = xmlschema.XMLSchema(XSD)


def validate(xml, schema=schema):
    if isinstance
    schema.validate(xml)


def to_dict(xml, schema=schema):
    return schema.to_dict(xml)
