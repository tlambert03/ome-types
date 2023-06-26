from typing import Any

from xsdata.codegen.models import Attr
from xsdata.formats.dataclass.filters import Filters
from xsdata.formats.dataclass.generator import DataclassGenerator
from xsdata.models.config import GeneratorConfig, OutputFormat
from xsdata_pydantic.generator import PydanticFilters

PRESERVED_NAMES = {"OME", "ROIRef", "XMLAnnotation", "ROI"}


class OmeGenerator(DataclassGenerator):
    @classmethod
    def init_filters(cls, config: GeneratorConfig) -> Filters:
        return OmeFilters(config)


class OmeFilters(PydanticFilters):
    def class_name(self, name: str) -> str:
        return name if name in PRESERVED_NAMES else super().class_name(name)

    def field_name(self, name: str, class_name: str) -> str:
        return super().field_name(name, class_name)

    @classmethod
    def build_class_annotation(cls, fmt: OutputFormat) -> str:
        # remove the @dataclass decorator
        return ""

    def field_definition(
        self,
        attr: Attr,
        ns_map: dict,
        parent_namespace: str | None,
        parents: list[str],
    ) -> str:
        """Return the field definition with any extra metadata."""
        # updated to use pydantic Field
        default_value = self.field_default_value(attr, ns_map)
        metadata = self.field_metadata(attr, parent_namespace, parents)

        kwargs: dict[str, Any] = {}
        if attr.fixed or attr.is_prohibited:
            kwargs["init"] = False

        if default_value is not False and not attr.is_prohibited:
            key = self.FACTORY_KEY if attr.is_factory else self.DEFAULT_KEY
            kwargs[key] = default_value

        if metadata:
            kwargs["metadata"] = metadata

        return f"Field({self.format_arguments(kwargs, 4)})"

    @classmethod
    def build_import_patterns(cls) -> dict[str, dict]:
        patterns = Filters.build_import_patterns()
        patterns.pop("dataclasses")
        patterns.update({"pydantic": {"Field": [" = Field("]}})

        return {key: patterns[key] for key in sorted(patterns)}
