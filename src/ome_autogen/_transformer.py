from xsdata.codegen.analyzer import ClassAnalyzer
from xsdata.codegen.container import ClassContainer, Steps
from xsdata.codegen.handlers import RenameDuplicateAttributes
from xsdata.codegen.models import Class
from xsdata.codegen.transformer import SchemaTransformer


class OMETransformer(SchemaTransformer):
    # overriding to remove the RenameDuplicateAttributes processor
    # we don't need it because we inject proper enum names _generator
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
