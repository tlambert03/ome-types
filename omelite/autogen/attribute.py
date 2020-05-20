from xmlschema import validators

from .component import ComponentConverter


class AttributeConverter(ComponentConverter):
    def __init__(self, component: validators.XsdAttribute):
        super().__init__(component)
        self.component = component

    @property
    def full_type_string(self) -> str:
        """full type, like Optional[List[str]]"""
        type_string = self.type_string
        if not type_string:
            return ""
        if self.is_optional:
            type_string = f"Optional[{type_string}]"
        return f": {type_string}" if type_string else ""
