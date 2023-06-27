from __future__ import annotations

import os
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from xml.etree import ElementTree as ET


@contextmanager
def cd(new_path: str | Path) -> Iterator[None]:
    prev = Path.cwd()
    os.chdir(Path(new_path).expanduser().absolute())
    try:
        yield
    finally:
        os.chdir(prev)


def get_plural_names(schema: Path | str) -> dict[str, str]:
    tree = ET.parse(schema)  # noqa: S314
    parents: list[ET.Element] = []
    names: dict[str, str] = {}
    for node in tree.iter():
        if "plural" in node.tag and node.text:
            names[parents[-4].attrib["name"]] = node.text
        parents.append(node)
    return names


CAMEL_SNAKE_OVERRIDES = {"ROIs": "rois"}
camel_snake_registry: dict[str, str] = {}


def camel_to_snake(name: str, **kwargs) -> str:
    name = name.lstrip("@")  # remove leading @ from "@any_element"
    result = CAMEL_SNAKE_OVERRIDES.get(name)
    if not result:
        # https://stackoverflow.com/a/1176023
        result = re.sub("([A-Z]+)([A-Z][a-z]+)", r"\1_\2", name)
        result = re.sub("([a-z0-9])([A-Z])", r"\1_\2", result)
        result = result.lower().replace(" ", "_")
    camel_snake_registry[name] = result
    return result
