from __future__ import annotations

from typing import TYPE_CHECKING

from xsdata.codegen.analyzer import ClassAnalyzer
from xsdata.codegen.container import ClassContainer, Steps
from xsdata.codegen.handlers import RenameDuplicateAttributes
from xsdata.codegen.transformer import SchemaTransformer

if TYPE_CHECKING:
    from xsdata.codegen.models import Class


class OMETransformer(SchemaTransformer):
    # overriding to remove the RenameDuplicateAttributes processor
    # we don't need it because we inject proper enum names in our _generator.py
    def analyze_classes(self, classes: list[Class]) -> list[Class]:
        """Analyzer the given class list and simplify attributes and extensions."""
        container = ClassContainer(config=self.config)

        santizers = container.processors[Steps.SANITIZE]
        for v in santizers:
            if isinstance(v, RenameDuplicateAttributes):
                santizers.remove(v)
                break

        container.extend(classes)

        return ClassAnalyzer.process(container)
