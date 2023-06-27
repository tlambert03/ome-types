from typing import List

from xsdata.codegen.models import Attr, Class
from xsdata.formats.dataclass.filters import Filters
from xsdata.formats.dataclass.generator import DataclassGenerator
from xsdata.models.config import GeneratorConfig
from xsdata_pydantic_basemodel.generator import PydanticBaseFilters

from . import _util


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
        return super().field_type(attr, parents)
