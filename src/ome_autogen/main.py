import subprocess
from pathlib import Path

from xsdata.codegen.transformer import SchemaTransformer
from xsdata.models.config import (
    CompoundFields,
    DocstringStyle,
    GeneratorConfig,
    GeneratorOutput,
    OutputFormat,
    StructureStyle,
)

from ome_autogen._generator import OmeGenerator
from ome_autogen._util import cd, resolve_source

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
        from xsdata.logger import logger

        logger.setLevel("DEBUG")

    output = GeneratorOutput(
        package=output_package,
        format=OutputFormat(value=OmeGenerator.KEY, slots=False),
        structure_style=StructureStyle.CLUSTERS,
        docstring_style=DocstringStyle.NUMPY,
        compound_fields=CompoundFields(enabled=False),
    )
    config = GeneratorConfig(output=output)

    uris = sorted(resolve_source(str(schema_file), recursive=False))
    transformer = SchemaTransformer(print=False, config=config)
    transformer.process_sources(uris)

    # xsdata doesn't support output path
    with cd(output_dir):
        transformer.process_classes()

    package_dir = Path(output_dir) / output_package.replace(".", "/")

    # Fix bug in xsdata output
    # https://github.com/tefra/xsdata/pull/806
    light_source = next(package_dir.rglob("light_source.py"))
    src = light_source.read_text()
    src = src.replace("UnitsPower.M_W,", "UnitsPower.M_W_1,")
    light_source.write_text(src)

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
