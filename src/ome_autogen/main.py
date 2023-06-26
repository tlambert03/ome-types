import subprocess
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from xsdata.codegen.transformer import SchemaTransformer
from xsdata.codegen.writer import CodeWriter
from xsdata.formats.dataclass.compat import class_types
from xsdata.logger import logger
from xsdata.models.config import (
    CompoundFields,
    DocstringStyle,
    ExtensionType,
    GeneratorConfig,
    GeneratorConventions,
    GeneratorExtension,
    GeneratorExtensions,
    GeneratorOutput,
    NameConvention,
    OutputFormat,
    StructureStyle,
)
from xsdata_pydantic.hooks import class_type, cli  # noqa: F401

from ome_autogen._util import camel_to_snake, cd, get_plural_names, resolve_source

from ._generator import OmeGenerator

SRC_PATH = Path(__file__).parent.parent
SCHEMA_FILE = SRC_PATH / "ome_types" / "ome-2016-06.xsd"
PACKAGE = f"ome_types2.model.{SCHEMA_FILE.stem.replace('-', '_')}"
RUFF_IGNORE: list[str] = [
    "D101",  # Missing docstring in public class
    "D106",  # Missing docstring in public nested class
    "D205",  # 1 blank line required between summary line and description
    "D404",  # First word of the docstring should not be This
    "E501",  # Line too long
    "S105",  # Possible hardcoded password
]

OME_BASE_EXTENSION = GeneratorExtension(
    type=ExtensionType.CLASS,
    class_name=".*",
    import_string="ome_types2.model._base_type.OMEType",
)


# These are critical to be able to use the format="OME"
OME_FORMAT = "OME"
CodeWriter.register_generator(OME_FORMAT, OmeGenerator)
from xsdata_pydantic.compat import Pydantic

class_types.register(OME_FORMAT, Pydantic())


class OmeNameCase(Enum):
    """Mimic the xsdata NameConvention enum, to modify snake case function.

    We want adjacent capital letters to remain caps.
    """

    OME_SNAKE = "omeSnakeCase"

    def __call__(self, string: str, **kwargs: Any) -> str:
        return self.callback(string, **kwargs)

    @property
    def callback(self) -> Callable:
        """Return the actual callable of the scheme."""
        return camel_to_snake


def convert_schema(
    output_dir: Path | str = SRC_PATH,
    schema_file: Path | str = SCHEMA_FILE,
    output_package: str = PACKAGE,
    debug: bool = False,
    line_length: int = 88,
    ruff_ignore: list[str] = RUFF_IGNORE,
    do_linting: bool = True,
) -> None:
    """Convert the OME schema to a python model."""
    if debug:
        logger.setLevel("DEBUG")

    config = GeneratorConfig(
        output=GeneratorOutput(
            package=output_package,
            format=OutputFormat(value="pydantic_base_model", slots=False),
            structure_style=StructureStyle.CLUSTERS,
            docstring_style=DocstringStyle.NUMPY,
            compound_fields=CompoundFields(enabled=False),
        ),
        # conventions=GeneratorConventions(
        #     field_name=NameConvention(OmeNameCase.OME_SNAKE, "value")
        # ),
        # extensions=GeneratorExtensions(extension=[OME_BASE_EXTENSION]),
    )

    uris = sorted(resolve_source(str(schema_file), recursive=False))
    transformer = SchemaTransformer(print=False, config=config)
    transformer.process_sources(uris)

    plurals = get_plural_names(schema=schema_file)

    # pluralize field names:
    for clazz in transformer.classes:
        for attr in clazz.attrs:
            if attr.is_list:
                # XXX: should we be adding s?
                attr.name = plurals.get(attr.name, f"{attr.name}")

    # xsdata doesn't support output path
    with cd(output_dir):
        transformer.process_classes()

    package_dir = Path(output_dir) / output_package.replace(".", "/")

    if not do_linting:
        print(f"\033[92m\033[1m✓ OME python model created at {output_package}\033[0m")
        return

    black = ["black", str(package_dir), "-q", f"--line-length={line_length}"]
    subprocess.check_call(black)  # noqa S

    ruff = ["ruff", "-q", "--fix", str(package_dir)]
    ruff.extend(f"--ignore={ignore}" for ignore in ruff_ignore)
    subprocess.check_call(ruff)  # noqa S

    mypy = ["mypy", str(package_dir), "--strict"]
    subprocess.check_output(mypy)  # noqa S

    # print a bold green checkmark
    print(f"\033[92m\033[1m✓ OME python model created at {output_package}\033[0m")
