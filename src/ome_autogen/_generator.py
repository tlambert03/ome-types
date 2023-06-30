from typing import List

from xsdata.codegen.models import Attr, Class
from xsdata.formats.dataclass.filters import Filters
from xsdata.formats.dataclass.generator import DataclassGenerator
from xsdata.models.config import GeneratorConfig
from xsdata.models.enums import DataType
from xsdata_pydantic_basemodel.generator import PydanticBaseFilters

from . import _util

AUTO_SEQUENCE = "__auto_sequence__"


class OmeGenerator(DataclassGenerator):
    @classmethod
    def init_filters(cls, config: GeneratorConfig) -> Filters:
        return OmeFilters(config)


class OmeFilters(PydanticBaseFilters):
    def __init__(self, config: GeneratorConfig):
        super().__init__(config)

        # FIXME: it would be nice to know how to get the schema we're processing from
        # the config.  For now, we just assume it's the OME schema and that's the
        # hardcoded default in _util.get_plural_names
        self.plurals = _util.get_plural_names()

    def class_bases(self, obj: Class, class_name: str) -> list[str]:
        # we don't need PydanticBaseFilters to add the Base class
        # because we add it in the config.extensions
        # This could go once PydanticBaseFilters is better about deduping
        return Filters.class_bases(self, obj, class_name)

    def field_type(self, attr: Attr, parents: List[str]) -> str:
        # HACK
        # It would be nicer to put this in the self.field_name method...but that
        # method only receives the attr name, not the attr object, and so we
        # don't know at that point whether it belongs to a list or not.
        # This hack works only because this method is called BEFORE self.field_name
        # in the class.jinja2 template, so we directly modify the attr object here.
        if attr.is_list:
            attr.name = self.plurals.get(attr.name, f"{attr.name}s")
        if self._is_color_attr(attr):
            return "Color"
        return super().field_type(attr, parents)

    @classmethod
    def build_import_patterns(cls) -> dict[str, dict]:
        patterns = super().build_import_patterns()
        patterns.update(
            {
                "ome_types.model._color": {
                    "Color": [": Color ="],
                }
            }
        )
        return {key: patterns[key] for key in sorted(patterns)}

    def field_default_value(self, attr: Attr, ns_map: dict | None = None) -> str:
        if attr.tag == "Attribute" and attr.name == "ID":
            return repr(AUTO_SEQUENCE)
        if self._is_color_attr(attr):
            return "Color"
        return super().field_default_value(attr, ns_map)

    def format_arguments(self, kwargs: dict, indent: int = 0) -> str:
        if kwargs.get("default") == "Color":
            # keep default_factory at the front
            kwargs = {"default_factory": kwargs.pop("default"), **kwargs}
        return super().format_arguments(kwargs, indent)

    def _is_color_attr(self, attr: Attr) -> bool:
        return attr.name == "Color" and attr.types[0].datatype == DataType.INT
