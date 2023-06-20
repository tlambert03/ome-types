import os
import subprocess
from pathlib import Path

from xsdata.cli import resolve_source
from xsdata.codegen.transformer import SchemaTransformer
from xsdata.logger import logger
from xsdata.models.config import (
    CompoundFields,
    DocstringStyle,
    GeneratorConfig,
    GeneratorOutput,
    OutputFormat,
    StructureStyle,
)

from ome_autogen._generator import OmeGenerator
from ome_autogen._util import _cd

SRC_PATH = Path(__file__).parent.parent
SCHEMA_FILE = SRC_PATH / "ome_types" / "ome-2016-06.xsd"
# PACKAGE = f'ome_types.model.{XSD.stem.replace("-", "_")}'
OUTPUT_PACKAGE = "ome_types.model"
OUTPUT_DIR = SRC_PATH / str(OUTPUT_PACKAGE).replace(".", os.path.sep)

# linting
LINE_LENGTH = 88
RUFF_IGNORE: list[str] = [
    "D101",  # Missing docstring in public class
    "D106",  # Missing docstring in public nested class
    "D205",  # 1 blank line required between summary line and description
    "D404",  # First word of the docstring should not be This
    "E501",  # Line too long
    "S105",  # Possible hardcoded password
]


if DEBUG := False:
    logger.setLevel("DEBUG")


output = GeneratorOutput(
    package=OUTPUT_PACKAGE,
    format=OutputFormat(value=OmeGenerator.KEY, slots=False),
    structure_style=StructureStyle.CLUSTERS,
    docstring_style=DocstringStyle.NUMPY,
    compound_fields=CompoundFields(enabled=False),
)
config = GeneratorConfig(output=output)

uris = sorted(resolve_source(str(SCHEMA_FILE), recursive=False))
transformer = SchemaTransformer(print=False, config=config)
transformer.process_sources(uris)

# xsdata doesn't support output path
with _cd(SRC_PATH):
    transformer.process_classes()


# Fix bug in xsdata output
# https://github.com/tefra/xsdata/pull/806
light_source = next(OUTPUT_DIR.rglob("light_source.py"))
src = light_source.read_text()
src = src.replace("UnitsPower.M_W,", "UnitsPower.M_W_1,")
light_source.write_text(src)


black = ["black", str(OUTPUT_DIR), "-q", f"--line-length={LINE_LENGTH}"]
subprocess.check_call(black)  # noqa S

ruff = ["ruff", "-q", "--fix", str(OUTPUT_DIR)]
ruff.extend(f"--ignore={ignore}" for ignore in RUFF_IGNORE)
subprocess.check_call(ruff)  # noqa S

mypy = ["mypy", str(OUTPUT_DIR), "--strict"]
subprocess.check_output(mypy)  # noqa S

# print a bold green checkmark
print(f"\033[92m\033[1m✓ OME python model created at {OUTPUT_PACKAGE}\033[0m")
