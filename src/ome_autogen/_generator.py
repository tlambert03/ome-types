from __future__ import annotations

import typing as typing_module
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, NamedTuple, cast

from xsdata.formats.dataclass.filters import Filters
from xsdata.formats.dataclass.generator import DataclassGenerator

from ome_autogen import _util
from ome_autogen.overrides import OVERRIDES
from xsdata_pydantic_basemodel.generator import PydanticBaseFilters

if TYPE_CHECKING:
    from jinja2 import Environment, FileSystemLoader
    from xsdata.codegen.models import Attr, Class
    from xsdata.codegen.resolver import DependenciesResolver
    from xsdata.models.config import GeneratorConfig


# classes that should never be optional, but always have default_factories
NEVER_OPTIONAL = {x for x in OVERRIDES if OVERRIDES[x].never_optional}
DEFAULTS = {x: d for x in OVERRIDES if (d := OVERRIDES[x].default) is not None}


class Override(NamedTuple):
    element_name: str  # name of the attribute in the XSD
    class_name: str  # name of our override class
    module_name: str | None  # module where the override class is defined


CLASS_OVERRIDES = [
    Override("FillColor", "Color", "ome_types.model._color"),
    Override("StrokeColor", "Color", "ome_types.model._color"),
    Override("Color", "Color", "ome_types.model._color"),
    # make the type annotation Non-Optional for structured annotations
    Override("StructuredAnnotations", "StructuredAnnotations", None),
]


# prebuilt maps for usage in code below
OVERRIDE_ELEM_TO_CLASS = {o.element_name: o.class_name for o in CLASS_OVERRIDES}
IMPORT_PATTERNS = {
    o.module_name: {
        o.class_name: [f": {o.class_name} =", f": Optional[{o.class_name}] ="]
    }
    for o in CLASS_OVERRIDES
    if o.module_name
}
IMPORT_PATTERNS.update(
    {
        "ome_types._mixins._util": {"new_uuid": ["default_factory=new_uuid"]},
        "datetime": {"datetime": ["datetime"]},
        "pydantic_compat": {
            "model_validator": ["model_validator("],
            "field_validator": ["field_validator("],
        },
        "ome_types._mixins._validators": {
            "any_elements_validator": ["any_elements_validator"],
            "bin_data_root_validator": ["bin_data_root_validator"],
            "pixel_type_to_numpy_dtype": ["pixel_type_to_numpy_dtype"],
            "pixels_root_validator": ["pixels_root_validator"],
            "validate_map_annotation": ["validate_map_annotation"],
            "validate_shape_union": ["validate_shape_union"],
            "validate_structured_annotations": ["validate_structured_annotations"],
            "xml_value_validator": ["xml_value_validator"],
        },
    }
)

# not all typing names appear to be added by xsdata
IMPORT_PATTERNS.setdefault("typing", {}).update(
    {n: [f": {n}"] for n in dir(typing_module) if not n.startswith("_")}
)


class OmeGenerator(DataclassGenerator):
    @classmethod
    def init_filters(cls, config: GeneratorConfig) -> Filters:
        return OmeFilters(config)

    def render_module(
        self, resolver: DependenciesResolver, classes: list[Class]
    ) -> str:
        mod = super().render_module(resolver, classes)

        # xsdata renames classes like "FillRule" (which appears as a SimpleType
        # inside of the Shape ComplexType) as "Shape_FillRule".
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


class OmeFilters(PydanticBaseFilters):
    def register(self, env: Environment) -> None:
        # add our own templates dir to the search path
        tpl_dir = Path(__file__).parent.joinpath("templates")
        cast("FileSystemLoader", env.loader).searchpath.insert(0, str(tpl_dir))
        super().register(env)
        env.filters.update({"methods": self.methods})

    def __init__(self, config: GeneratorConfig):
        super().__init__(config)

        # TODO: it would be nice to know how to get the schema we're processing from
        # the config.  For now, we just assume it's the OME schema and that's the
        # hardcoded default in _util.get_appinfo
        self.appinfo = _util.get_appinfo()

    @contextmanager
    def _modern_typing(self) -> Iterator[None]:
        """Context manager to use modern typing syntax."""
        prev_u, self.union_type = self.union_type, True
        prev_s, self.subscriptable_types = self.subscriptable_types, True
        try:
            yield
        finally:
            self.union_type = prev_u
            self.subscriptable_types = prev_s

    def class_params(self, obj: Class) -> Iterator[tuple[str, str, str]]:  # type: ignore[override]
        # This method override goes along with the docstring jinja template override
        # to fixup the numpy docstring format.
        # https://github.com/tefra/xsdata/issues/818
        # The type ignore is because xsdata returns an iterator of 2-tuples
        # but we want to return a 3-tuple.
        for attr in obj.attrs:
            name = attr.name
            name = (
                self.constant_name(name, obj.name)
                if obj.is_enumeration
                else self.field_name(name, obj.name)
            )
            with self._modern_typing():
                type_ = self.field_type(attr, [obj.name])
            help_ = attr.help
            if not help_:
                help_ = f"(The {obj.name} {attr.name})."
            yield name, type_, self.clean_docstring(help_)

    def class_bases(self, obj: Class, class_name: str) -> list[str]:
        # we don't need PydanticBaseFilters to add the Base class
        # because we add it in the config.extensions
        # This could go once PydanticBaseFilters is better about deduping
        return Filters.class_bases(self, obj, class_name)

    def _attr_is_optional(self, attr: Attr) -> bool:
        if attr.name in NEVER_OPTIONAL:
            return False
        return attr.is_nillable or (
            attr.default is None and (attr.is_optional or not self.format.kw_only)
        )

    def _format_type(self, attr: Attr, result: str) -> str:
        if self._attr_is_optional(attr):
            return f"None | {result}" if self.union_type else f"Optional[{result}]"
        return result

    def field_type(self, attr: Attr, parents: list[str]) -> str:
        if attr.is_list and not getattr(attr, "_plural_set", False):
            # HACK
            # It would be nicer to put this in the self.field_name method...but that
            # method only receives the attr name, not the attr object, and so we
            # don't know at that point whether it belongs to a list or not.
            # This hack works only because this method is called BEFORE self.field_name
            # in the class.jinja2 template, so we directly modify the attr object here.
            attr.name = self.appinfo.plurals.get(attr.name, f"{attr.name}s")
            attr._plural_set = True  # type: ignore

        if attr.name in OVERRIDE_ELEM_TO_CLASS:
            return self._format_type(attr, OVERRIDE_ELEM_TO_CLASS[attr.name])

        type_name = super().field_type(attr, parents)
        # we want to use datetime.datetime instead of XmlDateTime
        return type_name.replace("XmlDateTime", "datetime")

    @classmethod
    def build_import_patterns(cls) -> dict[str, dict]:
        patterns = super().build_import_patterns()
        patterns.setdefault("pydantic", {}).update(
            {
                "validator": ["validator("],
            }
        )
        patterns.update(IMPORT_PATTERNS)
        return {key: patterns[key] for key in sorted(patterns)}

    def field_default_value(self, attr: Attr, ns_map: dict | None = None) -> str:
        if attr.name in DEFAULTS:
            return DEFAULTS[attr.name]

        for override in CLASS_OVERRIDES:
            if attr.name == override.element_name:
                if not self._attr_is_optional(attr):
                    return override.class_name

        over = OVERRIDES.get(attr.name)
        if over and over.default_factory:
            return over.default_factory

        return super().field_default_value(attr, ns_map)

    def format_arguments(self, kwargs: dict, indent: int = 0) -> str:
        # keep default_factory at the front
        attr_name = kwargs["metadata"].get("name")
        override = OVERRIDES.get(attr_name)
        if override and override.default_factory:
            kwargs.pop("default", None)
            kwargs["default_factory"] = override.default_factory

        # uncomment this to use new_uuid as the default_factory for all UUIDs
        # but then we have an equality checking problem in the tests
        # if kwargs.get("metadata", {}).get("pattern", "").startswith("(urn:uuid:"):
        #     kwargs.pop("default", None)
        #     kwargs = {"default_factory": "new_uuid", **kwargs}
        return super().format_arguments(kwargs, indent)

    def constant_name(self, name: str, class_name: str) -> str:
        if class_name in self.appinfo.enums:
            # use the enum names found in appinfo/xsdfu/enum
            return self.appinfo.enums[class_name][name].enum
        return super().constant_name(name, class_name)

    def methods(self, obj: Class) -> list[str]:
        if obj.name in OVERRIDES and (lines := OVERRIDES[obj.name].add_lines):
            return ["\n\n" + "\n".join(lines)]
        return []
