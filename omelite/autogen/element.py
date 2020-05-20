from xmlschema import validators

from .component import ComponentConverter


class ElementConverter(ComponentConverter):
    def __init__(self, component: validators.XsdElement):
        super().__init__(component)
        self.component = component

    def get_imports(self):
        imports = super().get_imports()
        if not self.component.max_occurs:
            imports.add("from typing import List")

        if self.component.min_occurs == 0:
            if not self.component.max_occurs:
                imports.add("from dataclasses import field")
            else:
                imports.add("from typing import Optional")
        return imports

    @property
    def full_type_string(self) -> str:
        """full type, like Optional[List[str]]"""
        type_string = self.type_string
        if not type_string:
            return ""
        if not self.component.max_occurs:
            type_string = f"List[{type_string}]"
        if self.component.min_occurs == 0 and self.component.max_occurs == 1:
            type_string = f"Optional[{type_string}]"
        return f": {type_string}" if type_string else ""
