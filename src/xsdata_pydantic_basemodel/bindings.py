from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Generator,
    Iterator,
)
from xml.etree.ElementTree import QName

from xsdata.formats.dataclass import context, parsers, serializers
from xsdata.formats.dataclass.serializers import config
from xsdata.models.enums import QNames
from xsdata.utils import collections
from xsdata.utils.constants import EMPTY_MAP, return_input

if TYPE_CHECKING:
    from pydantic import BaseModel
    from xsdata.formats.dataclass.models.elements import XmlMeta


class XmlContext(context.XmlContext):
    """Pydantic BaseModel ready xml context instance."""

    def __init__(
        self,
        element_name_generator: Callable = return_input,
        attribute_name_generator: Callable = return_input,
    ):
        super().__init__(
            element_name_generator, attribute_name_generator, "pydantic-basemodel"
        )


class SerializerConfig(config.SerializerConfig):
    # here to add `ignore_unset_attributes` support to XmlSerializer
    __slots__ = (*config.SerializerConfig.__slots__, "ignore_unset_attributes")

    def __init__(self, **kwargs: Any) -> None:
        self.ignore_unset_attributes = kwargs.pop("ignore_unset_attributes", False)
        super().__init__(**kwargs)


@dataclass
class XmlParser(parsers.XmlParser):
    context: XmlContext = field(default_factory=XmlContext)


@dataclass
class XmlSerializer(serializers.XmlSerializer):
    context: XmlContext = field(default_factory=XmlContext)
    _config: ClassVar[config.SerializerConfig | None] = None

    def write_dataclass(
        self,
        obj: Any,
        namespace: str | None = None,
        qname: str | None = None,
        nillable: bool = False,
        xsi_type: str | None = None,
    ) -> Generator:
        # This is a hack to support `ignore_unset_attributes` in XmlSerializer
        # unforunately the `next_attribute` method is a class method and doesn't
        # have access to the instance config, so we have to temporarily set it as a
        # class variable and reset it after the method is called
        XmlSerializer._config = self.config
        try:
            yield from super().write_dataclass(
                obj, namespace, qname, nillable, xsi_type
            )
        finally:
            XmlSerializer._config = None

    # overriding so we can implement support for `ignore_unset_attributes`
    @classmethod
    def next_attribute(
        cls,
        obj: BaseModel,
        meta: XmlMeta,
        nillable: bool,
        xsi_type: str | None,
        ignore_optionals: bool,
    ) -> Iterator[tuple[str, Any]]:
        """
        Return the attribute variables with their object values if set and not
        empty iterables.

        :param obj: Input object
        :param meta: Object metadata
        :param nillable: Is model nillable
        :param xsi_type: The true xsi:type of the object
        :param ignore_optionals: Skip optional attributes with default
            value
        :return:
        """
        ignore_unset = getattr(cls._config, "ignore_unset_attributes", False)
        set_fields = obj.__fields_set__ if ignore_unset else set()

        for var in meta.get_attribute_vars():
            if var.is_attribute:
                value = getattr(obj, var.name)
                if (
                    value is None
                    or (collections.is_array(value) and not value)
                    or (ignore_optionals and var.is_optional(value))
                    or (ignore_unset and var.name not in set_fields)
                ):
                    continue

                yield var.qname, cls.encode(value, var)
            else:
                yield from getattr(obj, var.name, EMPTY_MAP).items()

        if xsi_type:
            yield QNames.XSI_TYPE, QName(xsi_type)

        if nillable:
            yield QNames.XSI_NIL, "true"


@dataclass
class JsonParser(parsers.JsonParser):
    context: XmlContext = field(default_factory=XmlContext)


@dataclass
class JsonSerializer(serializers.JsonSerializer):
    context: XmlContext = field(default_factory=XmlContext)


@dataclass
class UserXmlParser(parsers.UserXmlParser):
    context: XmlContext = field(default_factory=XmlContext)
