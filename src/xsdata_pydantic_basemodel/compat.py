import dataclasses as dc
from contextlib import suppress
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Type,
    TypeVar,
)

try:
    from lxml import etree as ET
except ImportError:
    import xml.etree.ElementTree as ET  # type: ignore

from pydantic import BaseModel, validators
from pydantic_compat import PYDANTIC2, PydanticCompatMixin
from xsdata.formats.dataclass.compat import Dataclasses, class_types
from xsdata.formats.dataclass.models.elements import XmlType
from xsdata.models.datatype import XmlDate, XmlDateTime, XmlDuration, XmlPeriod, XmlTime

from xsdata_pydantic_basemodel.pydantic_compat import Field, dataclass_fields

T = TypeVar("T", bound=object)

if TYPE_CHECKING:
    from pydantic import ConfigDict


class AnyElement(PydanticCompatMixin, BaseModel):
    """Generic model to bind xml document data to wildcard fields.

    :param qname: The element's qualified name
    :param text: The element's text content
    :param tail: The element's tail content
    :param children: The element's list of child elements.
    :param attributes: The element's key-value attribute mappings.
    """

    qname: Optional[str] = Field(default=None)
    text: Optional[str] = Field(default=None)
    tail: Optional[str] = Field(default=None)
    children: List["AnyElement"] = Field(
        default_factory=list,
        metadata={"type": XmlType.WILDCARD},  # type: ignore [call-arg,call-overload]
    )
    attributes: Dict[str, str] = Field(
        default_factory=dict,
        metadata={"type": XmlType.ATTRIBUTES},  # type: ignore [call-arg,call-overload]
    )

    model_config: ClassVar["ConfigDict"] = {"arbitrary_types_allowed": True}

    def to_etree_element(self) -> "ET._Element":
        elem = ET.Element(self.qname or "", self.attributes)
        elem.text = self.text
        elem.tail = self.tail
        for child in self.children:
            elem.append(child.to_etree_element())
        return elem


class DerivedElement(PydanticCompatMixin, BaseModel, Generic[T]):
    """Generic model wrapper for type substituted elements.

    Example: eg. <b xsi:type="a">...</b>

    :param qname: The element's qualified name
    :param value: The wrapped value
    :param type: The real xsi:type
    """

    qname: str
    value: T
    type: Optional[str] = None

    model_config: ClassVar["ConfigDict"] = {"arbitrary_types_allowed": True}


class PydanticBaseModel(Dataclasses):
    @property
    def any_element(self) -> Type:
        return AnyElement

    @property
    def derived_element(self) -> Type:
        return DerivedElement

    def is_model(self, obj: Any) -> bool:
        with suppress(Exception):
            clazz = obj if isinstance(obj, type) else type(obj)
            if issubclass(clazz, BaseModel) and clazz != BaseModel:
                rebuild = getattr(clazz, "model_rebuild", None)
                if callable(rebuild):
                    rebuild()
                return True
        return False

    #
    # https://github.com/tefra/xsdata/pull/949
    def get_fields(self, obj: Any) -> Iterator[dc.Field]:  # type: ignore[override]
        yield from dataclass_fields(obj)


class_types.register("pydantic-basemodel", PydanticBaseModel())


def make_validators(tp: Type, factory: Callable) -> List[Callable]:
    def validator(value: Any) -> Any:
        if isinstance(value, tp):
            return value

        if isinstance(value, str):
            return factory(value)

        raise ValueError

    return [validator]


_validators = {
    XmlDate: make_validators(XmlDate, XmlDate.from_string),
    XmlDateTime: make_validators(XmlDateTime, XmlDateTime.from_string),
    XmlTime: make_validators(XmlTime, XmlTime.from_string),
    XmlDuration: make_validators(XmlDuration, XmlDuration),
    XmlPeriod: make_validators(XmlPeriod, XmlPeriod),
    ET.QName: make_validators(ET.QName, ET.QName),
}

if not PYDANTIC2:
    validators._VALIDATORS.extend(list(_validators.items()))
else:
    from pydantic import BaseModel
    from pydantic_core import core_schema as cs

    def _make_get_core_schema(validator: Callable) -> Callable:
        def get_core_schema(*args: Any) -> cs.PlainValidatorFunctionSchema:
            return cs.general_plain_validator_function(validator)

        return get_core_schema

    for type_, val in _validators.items():
        get_schema = _make_get_core_schema(val[0])
        with suppress(TypeError):
            type_.__get_pydantic_core_schema__ = get_schema  # type: ignore
