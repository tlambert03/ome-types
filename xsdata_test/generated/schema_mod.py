from dataclasses import dataclass, field
from typing import Optional

from generated._base import MyMixin

__NAMESPACE__ = "http://xsdata"


@dataclass(repr=False)
class Foo(MyMixin):
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(urn:lsid:([\w\-\.]+\.[\w\-\.]+)+:\S+:\S+)|(\S+:\S+)",
        },
    )


@dataclass(repr=False)
class Root(MyMixin):
    foo: Optional[Foo] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://xsdata",
        },
    )
