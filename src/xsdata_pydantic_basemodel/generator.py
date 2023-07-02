from __future__ import annotations

from typing import TYPE_CHECKING

from xsdata.formats.dataclass.filters import Filters
from xsdata.formats.dataclass.generator import DataclassGenerator
from xsdata.utils.collections import unique_sequence
from xsdata.utils.text import stop_words

if TYPE_CHECKING:
    from xsdata.codegen.models import Attr, Class
    from xsdata.models.config import GeneratorConfig, OutputFormat

stop_words.update(("schema", "validate"))


class PydanticBaseGenerator(DataclassGenerator):
    """Python pydantic dataclasses code generator."""

    @classmethod
    def init_filters(cls, config: GeneratorConfig) -> Filters:
        return PydanticBaseFilters(config)


class PydanticBaseFilters(Filters):
    @classmethod
    def build_import_patterns(cls) -> dict[str, dict]:
        patterns = Filters.build_import_patterns()
        patterns.update(
            {
                "pydantic": {
                    "Field": [" = Field("],
                    "BaseModel": ["BaseModel"],
                }
            }
        )
        return {key: patterns[key] for key in sorted(patterns)}

    @classmethod
    def build_class_annotation(cls, fmt: OutputFormat) -> str:
        # remove the @dataclass decorator
        return ""

    def field_definition(
        self, attr: Attr, ns_map: dict, parent_namespace: str | None, parents: list[str]
    ) -> str:
        defn = super().field_definition(attr, ns_map, parent_namespace, parents)
        return defn.replace("field(", "Field(")

    def format_arguments(self, kwargs: dict, indent: int = 0) -> str:
        # called by field_definition
        self.move_metadata_to_pydantic_field(kwargs)
        return super().format_arguments(kwargs, indent)

    def class_bases(self, obj: Class, class_name: str) -> list[str]:
        # add BaseModel to the class bases
        # FIXME ... need to dedupe superclasses
        bases = super().class_bases(obj, class_name)
        return unique_sequence([*bases, "BaseModel"])

    def move_metadata_to_pydantic_field(self, kwargs: dict, pop: bool = False) -> None:
        """Move metadata from the metadata dict to the pydantic Field kwargs."""
        # XXX: can we pop them?  or does xsdata need them in the metdata dict as well?
        if "metadata" not in kwargs:  # pragma: no cover
            return

        metadata: dict = kwargs["metadata"]
        getitem = metadata.pop if pop else metadata.get
        for from_, to_ in [
            ("min_inclusive", "ge"),
            ("min_exclusive", "gt"),
            ("max_inclusive", "le"),
            ("max_exclusive", "lt"),
            ("min_occurs", "min_items"),
            ("max_occurs", "max_items"),
            ("pattern", "regex"),
            ("min_length", "min_length"),
            ("max_length", "max_length"),
        ]:
            if from_ in metadata:
                kwargs[to_] = getitem(from_)
