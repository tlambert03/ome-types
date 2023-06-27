from xsdata.codegen.models import Class
from xsdata.formats.dataclass.filters import Filters
from xsdata.formats.dataclass.generator import DataclassGenerator
from xsdata.models.config import GeneratorConfig
from xsdata_pydantic_basemodel.generator import PydanticBaseFilters

PRESERVED_NAMES = {"OME", "ROIRef", "XMLAnnotation", "ROI"}


class OmeGenerator(DataclassGenerator):
    @classmethod
    def init_filters(cls, config: GeneratorConfig) -> Filters:
        return OmeFilters(config)


class OmeFilters(PydanticBaseFilters):
    def class_name(self, name: str) -> str:
        return name if name in PRESERVED_NAMES else super().class_name(name)

    def class_bases(self, obj: Class, class_name: str) -> list[str]:
        # we don't need PydanticBaseFilters to add the Base class
        # because we add it in the config.extensions
        return Filters.class_bases(self, obj, class_name)
