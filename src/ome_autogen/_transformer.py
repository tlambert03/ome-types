from __future__ import annotations

from typing import TYPE_CHECKING

from xsdata.codegen.analyzer import ClassAnalyzer
from xsdata.codegen.container import ClassContainer
from xsdata.codegen.handlers import RenameDuplicateAttributes, UnnestInnerClasses
from xsdata.codegen.transformer import SchemaTransformer

if TYPE_CHECKING:
    from xsdata.codegen.models import Class


class UnnestInnerClassesWithoutRenaming(UnnestInnerClasses):
    def process(self, target: Class) -> None:
        for inner in list(target.inner):
            # do it even if it's an enumeration
            # if inner.is_enumeration or self.container.config.output.unnest_classes:
            if self.container.config.output.unnest_classes:
                self.promote(target, inner)

    @classmethod
    def clone_class(cls, inner: Class, name: str) -> Class:
        clone = inner.clone()
        clone.local_type = True
        # this is the reason we're overriding this method
        # clone.qname = build_qname(inner.target_namespace, f"{name}_{inner.name}")
        return clone


UNWANTED_HANDLERS = (
    # we don't need RenameDuplicateAttributes because we inject
    # proper enum names in our _generator.py
    (RenameDuplicateAttributes, None),
    # this is the one that converts inner classes to:
    # Channel.AcquisitionMode -> Channel_AcquisitionMode
    # when inner.is_enumeration or self.container.config.output.unnest_classes:
    # (UnnestInnerClasses, UnnestInnerClassesWithoutRenaming),
)


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
