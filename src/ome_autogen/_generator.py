from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from xsdata.formats.dataclass.filters import Filters
from xsdata.formats.dataclass.generator import DataclassGenerator

from ome_autogen import _util
from xsdata_pydantic_basemodel.generator import PydanticBaseFilters

if TYPE_CHECKING:
    from xsdata.codegen.models import Attr, Class
    from xsdata.codegen.resolver import DependenciesResolver
    from xsdata.models.config import GeneratorConfig


# from ome_types._mixins._base_type import AUTO_SEQUENCE
# avoiding import to avoid build-time dependency on the ome-types package
AUTO_SEQUENCE = "__auto_sequence__"


class OmeGenerator(DataclassGenerator):
    @classmethod
    def init_filters(cls, config: GeneratorConfig) -> Filters:
        return OmeFilters(config)

    def render_module(
        self, resolver: DependenciesResolver, classes: list[Class]
    ) -> str:
        mod = super().render_module(resolver, classes)

        # xsdata renames classes like "FillRule" (which appears as a SimpleType
        # inside of the Shape ComlexType) as "Shape_FillRule".
        # We want to make them available as "FillRule" in the corresponding
        # module, (i.e. the "Shape" module in this case).
        # That is, we want "Shape = Shape_FillRule" included in the module.
        # this is for backwards compatibility.
        aliases = []
        for c in classes:
            for i in resolver.imports:
                if f"{c.name}_" in i.qname:
                    # import_name is something like 'Shape_FillRule'
                    import_name = i.qname.rsplit("}", 1)[-1]
                    # desired alias is just 'FillRule'
                    alias = import_name.split(f"{c.name}_")[-1]
                    aliases.append(f"{alias} = {import_name}")

            # we also want inner (nested) classes to be available at the top level
            # e.g. map.Map.M -> map.M
            for inner in c.inner:
                aliases.append(f"{inner.name} = {c.name}.{inner.name}")

        if aliases:
            mod += "\n\n" + "\n".join(aliases) + "\n"

        return mod


class Override(NamedTuple):
    element_name: str
    class_name: str
    module_name: str | None


CLASS_OVERRIDES = [
    Override("Color", "Color", "ome_types.model._color"),
    Override("Union", "ShapeUnion", "ome_types.model._shape_union"),
    Override("StructuredAnnotations", "StructuredAnnotations", None),
]


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

        for override in CLASS_OVERRIDES:
            if attr.name == override.element_name:
                return override.class_name
        return super().field_type(attr, parents)

    @classmethod
    def build_import_patterns(cls) -> dict[str, dict]:
        patterns = super().build_import_patterns()
        patterns.update(
            {
                o.module_name: {o.class_name: [f": {o.class_name} ="]}
                for o in CLASS_OVERRIDES
                if o.module_name
            }
        )
        return {key: patterns[key] for key in sorted(patterns)}

    def field_default_value(self, attr: Attr, ns_map: dict | None = None) -> str:
        if attr.tag == "Attribute" and attr.name == "ID":
            return repr(AUTO_SEQUENCE)
        for override in CLASS_OVERRIDES:
            if attr.name == override.element_name:
                return override.class_name
        return super().field_default_value(attr, ns_map)

    def format_arguments(self, kwargs: dict, indent: int = 0) -> str:
        # keep default_factory at the front
        factorize = [x.class_name for x in CLASS_OVERRIDES] + ["StructuredAnnotations"]
        if kwargs.get("default") in factorize:
            kwargs = {"default_factory": kwargs.pop("default"), **kwargs}

        return super().format_arguments(kwargs, indent)

    def constant_name(self, name: str, class_name: str) -> str:
        if class_name in self.appinfo.enums:
            # use the enum names found in appinfo/xsdfu/enum
            return self.appinfo.enums[class_name][name].enum
        return super().constant_name(name, class_name)
