from xsdata.codegen.writer import CodeWriter
from xsdata.formats.dataclass.filters import Filters
from xsdata.models.config import GeneratorConfig
from xsdata_pydantic.generator import PydanticFilters, PydanticGenerator

PRESERVED_NAMES = {"OME", "ROIRef", "XMLAnnotation", "ROI"}


class OmeGenerator(PydanticGenerator):
    """Python pydantic dataclasses code generator."""

    KEY = "ome"

    @classmethod
    def init_filters(cls, config: GeneratorConfig) -> Filters:
        return OmeFilters(config)


class OmeFilters(PydanticFilters):
    def class_name(self, name: str) -> str:
        return name if name in PRESERVED_NAMES else super().class_name(name)

    def field_name(self, name: str, class_name: str) -> str:
        return super().field_name(name, class_name)


CodeWriter.register_generator(OmeGenerator.KEY, OmeGenerator)
