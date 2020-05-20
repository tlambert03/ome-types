import re
from os.path import dirname, join, exists
from typing import Dict
import pickle
import xmlschema

__cache__: Dict[str, xmlschema.XMLSchema] = {}


def get_schema(xml):
    url = xmlschema.fetch_schema(xml)
    match = re.search(r"\d{4}-\d{2}", url)
    version = match.group() if match else url
    if version not in __cache__:
        local = join(dirname(__file__), f"{version}.pkl")
        if exists(local):
            with open(local, "rb") as f:
                __cache__[version] = pickle.load(f)
        else:
            __cache__[version] = xmlschema.XMLSchema(url)
            with open(local, "wb") as f:
                pickle.dump(__cache__[version], f)
    return __cache__[version]


def validate(xml: str, schema=None):
    schema = schema or get_schema(xml)
    schema.validate(xml)


def to_dict(xml: str, schema=None):
    schema = schema or get_schema(xml)
    return schema.to_dict(xml)
