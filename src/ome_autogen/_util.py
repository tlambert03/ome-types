from __future__ import annotations

import os
import re
from collections import defaultdict
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator, NamedTuple, cast
from xml.etree import ElementTree as ET

SRC_PATH = Path(__file__).parent.parent
SCHEMA_FILE = (SRC_PATH / "ome_types" / "ome-2016-06.xsd").absolute()


@contextmanager
def cd(new_path: str | Path) -> Iterator[None]:
    """Temporarily change the current working directory.

    Used as a workaround for xsdata not supporting output path.
    """
    prev = Path.cwd()
    os.chdir(Path(new_path).expanduser().absolute())
    try:
        yield
    finally:
        os.chdir(prev)


class EnumInfo(NamedTuple):
    name: str
    plural: str
    unitsystem: str
    enum: str


class AppInfo(NamedTuple):
    plurals: dict[str, str]
    enums: dict[str, dict[str, EnumInfo]]
    abstract: list[str]


@lru_cache(maxsize=None)
def get_appinfo(schema: Path | str = SCHEMA_FILE) -> AppInfo:
    """Gather all the <xsd:appinfo> stuff from the schema.

    xsdata doesn't try to do anything with it. But we want to use it to
    provide better enum and plural names
    """
    tree = ET.parse(schema)
    plurals: dict[str, str] = {}
    enums: defaultdict[str, dict[str, EnumInfo]] = defaultdict(dict)
    in_name = ""
    in_value = ""
    abstract = []
    for node in tree.iter():
        if node.tag == "plural":  # <plural>
            plurals[in_name] = cast(str, node.text)
        elif node.tag == "enum":  # <enum>
            enums[in_name][in_value] = EnumInfo(
                node.get("name", ""),
                node.get("plural", ""),
                node.get("unitsystem", ""),
                node.get("enum", ""),
            )
        elif node.tag == "abstract":  # <abstract>
            abstract.append(in_name)
        else:
            in_name = node.get("name", in_name)
            in_value = node.get("value", in_value)

    return AppInfo(plurals, dict(enums), abstract)


CAMEL_SNAKE_OVERRIDES = {"ROIs": "rois"}
camel_snake_registry: dict[str, str] = {}


def camel_to_snake(name: str, **kwargs: Any) -> str:
    """Variant of camel_to_snake that preserves adjacent uppercase letters.

    https://stackoverflow.com/a/1176023
    """
    name = name.lstrip("@")  # remove leading @ from "@any_element"
    result = CAMEL_SNAKE_OVERRIDES.get(name)
    if not result:
        result = re.sub("([A-Z]+)([A-Z][a-z]+)", r"\1_\2", name)
        result = re.sub("([a-z0-9])([A-Z])", r"\1_\2", result)
        result = result.lower().replace(" ", "_")
    camel_snake_registry[name] = result
    return result
