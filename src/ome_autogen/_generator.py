from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from xsdata.formats.dataclass.filters import Filters
from xsdata.formats.dataclass.generator import DataclassGenerator
from xsdata.models.enums import DataType
from xsdata_pydantic_basemodel.generator import PydanticBaseFilters

from ome_autogen import _util

if TYPE_CHECKING:
    from xsdata.codegen.models import Attr, Class
    from xsdata.codegen.resolver import DependenciesResolver
    from xsdata.models.config import GeneratorConfig


# from ome_types._mixins._base_type import AUTO_SEQUENCE
# avoiding import to avoid build-time dependency on the ome-types package
AUTO_SEQUENCE = "__auto_sequence__"


ENUM_GETATTR_WARNING = """
def __getattr__(name: str) -> Any:
    _map = {map}
    if name in _map:
        import warnings

        cls = globals()[_map[name]]

        warnings.warn(
            f"Accessing {{name!r}} at the top level of {{__name__!r}} is deprecated. "
            f"Please access it through {{cls.__name__}}.{{name}} instead.",
            stacklevel=2,
        )

        return getattr(cls, name)
    raise AttributeError(f"module {{__name__!r}} has no attribute {{name!r}}")
"""


def make_gettattr(parents: dict[str, list[str]]) -> str:
    children = {c: p for p, cs in parents.items() for c in cs}
    return ENUM_GETATTR_WARNING.format(map=repr(children))


def make_aliases(parents: dict[str, list[str]]) -> str:
    out = []
    for p, cs in parents.items():
        for c in cs:
            out.append(f"{c} = {p}.{c}")

    return "\n".join(out)


class OmeGenerator(DataclassGenerator):
    @classmethod
    def init_filters(cls, config: GeneratorConfig) -> Filters:
        return OmeFilters(config)

    def render_module(
        self, resolver: DependenciesResolver, classes: list[Class]
    ) -> str:
        mod = super().render_module(resolver, classes)

        # Here, we look for nested enums, and make them accessible at the top level
        # of the module as well, with a deprecation warning.
        parents: dict[str, list[str]] = {}
        for node in ast.parse(mod).body:
            if isinstance(node, ast.ClassDef):
                for subnode in node.body:
                    if isinstance(subnode, ast.ClassDef) and subnode.name != "Meta":
                        parent = parents.setdefault(node.name, [])
                        parent.append(subnode.name)
        if parents:
            # extra = make_gettattr(parents)
            extra = make_aliases(parents)
            mod = "from typing import Any\n" + mod + "\n\n" + extra

        return mod


class OmeFilters(PydanticBaseFilters):
    def __init__(self, config: GeneratorConfig):
        super().__init__(config)

        # TODO: it would be nice to know how to get the schema we're processing from
        # the config.  For now, we just assume it's the OME schema and that's the
        # hardcoded default in _util.get_appinfo
        self.appinfo = _util.get_appinfo()

    def class_bases(self, obj: Class, class_name: str) -> list[str]:
        # we don't need PydanticBaseFilters to add the Base class
        # because we add it in the config.extensions
        # This could go once PydanticBaseFilters is better about deduping
        return Filters.class_bases(self, obj, class_name)

    def field_type(self, attr: Attr, parents: list[str]) -> str:
        # HACK
        # It would be nicer to put this in the self.field_name method...but that
        # method only receives the attr name, not the attr object, and so we
        # don't know at that point whether it belongs to a list or not.
        # This hack works only because this method is called BEFORE self.field_name
        # in the class.jinja2 template, so we directly modify the attr object here.
        if attr.is_list:
            attr.name = self.appinfo.plurals.get(attr.name, f"{attr.name}s")
        if self._is_color_attr(attr):
            return "Color"
        elif self._is_union_attr(attr):
            return "ShapeUnion"

        return super().field_type(attr, parents)

    @classmethod
    def build_import_patterns(cls) -> dict[str, dict]:
        patterns = super().build_import_patterns()
        patterns.update(
            {
                "ome_types.model._color": {"Color": [": Color ="]},
                "ome_types.model._roi_union": {"ShapeUnion": [": ShapeUnion ="]},
            }
        )
        return {key: patterns[key] for key in sorted(patterns)}

    def field_default_value(self, attr: Attr, ns_map: dict | None = None) -> str:
        if attr.tag == "Attribute" and attr.name == "ID":
            return repr(AUTO_SEQUENCE)
        if self._is_color_attr(attr):
            return "Color"
        if self._is_union_attr(attr):
            return "ShapeUnion"
        return super().field_default_value(attr, ns_map)

    def format_arguments(self, kwargs: dict, indent: int = 0) -> str:
        # keep default_factory at the front
        if kwargs.get("default") == "Color":
            kwargs = {"default_factory": kwargs.pop("default"), **kwargs}
        if kwargs.get("default") == "ShapeUnion":
            kwargs = {"default_factory": kwargs.pop("default"), **kwargs}
        return super().format_arguments(kwargs, indent)

    def constant_name(self, name: str, class_name: str) -> str:
        if class_name in self.appinfo.enums:
            # use the enum names found in appinfo/xsdfu/enum
            return self.appinfo.enums[class_name][name].enum
        return super().constant_name(name, class_name)

    def _is_color_attr(self, attr: Attr) -> bool:
        # special logic to find Color types, for which we use our own type.
        return attr.name == "Color" and attr.types[0].datatype == DataType.INT

    def _is_union_attr(self, attr: Attr) -> bool:
        # special logic to find Color types, for which we use our own type.
        return attr.name == "Union" and attr.types[0].substituted
