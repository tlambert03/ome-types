from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator

from xsdata.codegen.analyzer import ClassAnalyzer
from xsdata.codegen.container import ClassContainer
from xsdata.codegen.handlers import RenameDuplicateAttributes
from xsdata.codegen.mappers.schema import SchemaMapper

if TYPE_CHECKING:
    from xsdata.codegen.transformer import ResourceTransformer

else:
    try:
        from xsdata.codegen.transformer import ResourceTransformer
    except ImportError:
        from xsdata.codegen.transformer import SchemaTransformer as ResourceTransformer

from xsdata.models.xsd import Attribute

if TYPE_CHECKING:
    from xsdata.codegen.models import Class
    from xsdata.models.xsd import Schema


# we don't need RenameDuplicateAttributes because we inject
# proper enum names in our _generator.py
UNWANTED_HANDLERS = [RenameDuplicateAttributes]


def display_help(self: Attribute) -> str | None:
    """Monkeypatched display_help to also mine simple_type.annotations for docs."""
    help_str = super(Attribute, self).display_help

    if not help_str and self.simple_type is not None:
        help_str = "\n".join(
            doc.tostring() or ""
            for annotation in self.simple_type.annotations
            for doc in annotation.documentations
        ).strip()

    return help_str or None


@contextmanager
def monkeypatched_display_help() -> Iterator[None]:
    prev = Attribute.display_help
    Attribute.display_help = property(display_help)  # type: ignore
    try:
        yield
    finally:
        Attribute.display_help = prev  # type: ignore


class OMESchemaMapper(SchemaMapper):
    # may not need to override this... but here just in case
    pass


class OMETransformer(ResourceTransformer):
    # overriding to use our own schema mapper
    def generate_classes(self, schema: Schema) -> list[Class]:
        """Convert the given schema tree to a list of classes."""
        with monkeypatched_display_help():
            return OMESchemaMapper.map(schema)

    # overriding to remove the certain handlers
    def analyze_classes(self, classes: list[Class]) -> list[Class]:
        """Analyzer the given class list and simplify attributes and extensions."""
        # xsdata makes this particular class hard to extend/modify
        container = ClassContainer(config=self.config)

        for handlers in container.processors.values():
            for h in list(handlers):
                for unwanted in UNWANTED_HANDLERS:
                    if isinstance(h, unwanted):
                        handlers.remove(h)

        container.extend(classes)

        return ClassAnalyzer.process(container)
