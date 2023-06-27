from enum import Enum
from typing import Any

from xsdata.codegen.writer import CodeWriter
from xsdata.models import config as cfg
from xsdata.utils import text

from ome_autogen._util import camel_to_snake

from ._generator import OmeGenerator

OME_BASE_TYPE = "ome_types2.model._base_type.OMEType"
OUTPUT_PACKAGE = "ome_types2.model.ome_2016_06"
OME_FORMAT = "OME"


#  critical to be able to use the format="OME"
CodeWriter.register_generator(OME_FORMAT, OmeGenerator)


class OmeNameCase(Enum):
    """Mimic the xsdata NameConvention enum, to modify snake case function.

    We want adjacent capital letters to remain caps.
    """

    OME_SNAKE = "omeSnakeCase"

    def __call__(self, string: str, **kwargs: Any) -> str:
        return camel_to_snake(string, **kwargs)

    # @property
    # def callback(self) -> Callable:
    #     """Return the actual callable of the scheme."""
    #     return camel_to_snake


def get_config() -> cfg.GeneratorConfig:
    # ALLOW "type" to be used as a field name
    text.stop_words.discard("type")

    # add our own base type to every class
    ome_extension = cfg.GeneratorExtension(
        type=cfg.ExtensionType.CLASS,
        class_name=".*",
        import_string=OME_BASE_TYPE,
    )

    # our own snake case convention
    ome_convention = cfg.NameConvention(OmeNameCase.OME_SNAKE, "value")  # type: ignore

    return cfg.GeneratorConfig(
        output=cfg.GeneratorOutput(
            package=OUTPUT_PACKAGE,
            # format.value lets us use our own generator
            # kw_only is important, it makes required fields actually be required
            format=cfg.OutputFormat(value=OME_FORMAT, kw_only=True),
            structure_style=cfg.StructureStyle.CLUSTERS,
            docstring_style=cfg.DocstringStyle.NUMPY,
            compound_fields=cfg.CompoundFields(enabled=True, default_name="choice"),
        ),
        extensions=cfg.GeneratorExtensions([ome_extension]),
        conventions=cfg.GeneratorConventions(field_name=ome_convention),
    )
