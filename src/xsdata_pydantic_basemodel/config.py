from dataclasses import dataclass
from typing import Literal

from xsdata.models import config


@dataclass
class GeneratorOutput(config.GeneratorOutput):
    # v1 will only support pydantic<2
    # v2 will only support pydantic>=2
    # auto will only support whatever pydantic is installed at codegen time
    # both will support both pydantic versions
    pydantic_support: Literal["v1", "v2", "auto", "both"] = "auto"

    def __post_init__(self) -> None:
        if self.pydantic_support not in ("v1", "v2", "auto", "both"):
            raise ValueError(
                "pydantic_support must be one of 'v1', 'v2', 'auto', 'both', not "
                f"{self.pydantic_support!r}"
            )
