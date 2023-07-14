from dataclasses import dataclass

from xsdata.models import config


@dataclass
class GeneratorOutput(config.GeneratorOutput):
    pydantic_cross_compatible: bool = False
