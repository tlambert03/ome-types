import re
from xmlschema import qnames

import black
import isort


def black_format(text, line_length=79):
    return black.format_str(text, mode=black.FileMode(line_length=line_length))


def sort_imports(text):
    return isort.SortImports(file_contents=text).output


def clean(s):
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


def print_attrs(e):
    for n in dir(e):
        if n.startswith(("_", "tostring")):
            continue
        try:
            m = getattr(e, n)
            if callable(m):
                m = m()
            print(f"{n:20}", m)
        except Exception:
            pass


type_name_lookup = {
    "string": "str",
    "float": "float",
    "double": "float",
    "decimal": "float",
    "dateTime": "datetime",
    "long": "int",
    "int": "int",
    "anyURI": "str",
    "boolean": "bool",
}


def props_sorter(props):
    return ("" if "=" in props else "   ") + props.lower()


def make_enum(component, name=None):
    name = name or component.local_name
    lines = ["from enum import Enum", "", ""]
    lines += [f"class {name}(Enum):"]
    is_str = type_name_lookup[component.base_type.local_name] == "str"
    enum_elems = list(component.elem.iter("enum"))
    facets = component.get_facet(qnames.XSD_ENUMERATION)
    if enum_elems:
        for el, value in zip(enum_elems, facets.enumeration):
            name = el.attrib["enum"]
            if is_str:
                value = f'"{value}"'
            lines.append(f"    {name} = {value}")
            # # aliases
            # if el.attrib.get('name', False):
            #     value = el.attrib.get('name')
            #     if is_str:
            #         value = f'"{value}"'
            #     lines.append(f"    {name}_ALIAS = {value}")
    else:
        for e in facets.enumeration:
            lines.append(f"    {clean(camel_to_snake(e))} = '{e}'")
    return "\n".join(lines) + "\n"


def convert_pattern_facet(facet):
    assert len(facet.regexps) == 1, "Cannot handle pattern facet other than length = 1"
    return f"regex = re.compile(r'{facet.regexps[0]}')"


def convert_min_inclusive_facet(facet):
    return f"ge = {facet.value}"


def convert_min_exclusive_facet(facet):
    return f"gt = {facet.value}"


def convert_max_inclusive_facet(facet):
    return f"le = {facet.value}"


def convert_max_exclusive_facet(facet):
    return f"lt = {facet.value}"


facet_converters = {
    qnames.XSD_PATTERN: convert_pattern_facet,
    qnames.XSD_MIN_INCLUSIVE: convert_min_inclusive_facet,
    qnames.XSD_MIN_EXCLUSIVE: convert_min_exclusive_facet,
    qnames.XSD_MAX_INCLUSIVE: convert_max_inclusive_facet,
    qnames.XSD_MAX_EXCLUSIVE: convert_max_exclusive_facet,
}
