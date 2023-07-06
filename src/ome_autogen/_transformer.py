from __future__ import annotations

from typing import TYPE_CHECKING

from xsdata.codegen.analyzer import ClassAnalyzer
from xsdata.codegen.container import ClassContainer
from xsdata.codegen.handlers import RenameDuplicateAttributes
from xsdata.codegen.transformer import SchemaTransformer

if TYPE_CHECKING:
    from xsdata.codegen.models import Class


# we don't need RenameDuplicateAttributes because we inject
# proper enum names in our _generator.py
UNWANTED_HANDLERS = [(RenameDuplicateAttributes, None)]


class OMETransformer(SchemaTransformer):
    # overriding to remove the certain handlers
    def analyze_classes(self, classes: list[Class]) -> list[Class]:
        """Analyzer the given class list and simplify attributes and extensions."""
        # xsdata makes this particular class hard to extend/modify
        container = ClassContainer(config=self.config)

        for handlers in container.processors.values():
            for idx, h in enumerate(list(handlers)):
                for unwanted, wanted in UNWANTED_HANDLERS:
                    if isinstance(h, unwanted):
                        handlers.remove(h)
                        if wanted is not None:
                            handlers.insert(idx, wanted(container))

        container.extend(classes)

        return ClassAnalyzer.process(container)
