import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

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

XSD = Path(__file__).parent / "ome_types" / "ome-2016-06.xsd"
SRC = Path(__file__).parent
# PACKAGE = f'ome_types.model.{XSD.stem.replace("-", "_")}'
PACKAGE = "ome_types.model"
PACKAGE_PATH = SRC / str(PACKAGE).replace(".", os.path.sep)
OUTPUT_FORMAT = "pydantic"
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


@contextmanager
def _cd(new_path: str | Path) -> Iterator[None]:
    prev = Path.cwd()
    os.chdir(Path(new_path).expanduser().absolute())
    try:
        yield
    finally:
        os.chdir(prev)


output = GeneratorOutput(
    package=PACKAGE,
    format=OutputFormat(value=OUTPUT_FORMAT, slots=False),
    structure_style=StructureStyle.CLUSTERS,
    docstring_style=DocstringStyle.NUMPY,
    compound_fields=CompoundFields(enabled=False),
)
config = GeneratorConfig(output=output)

uris = sorted(resolve_source(str(XSD), recursive=False))
transformer = SchemaTransformer(print=False, config=config)
transformer.process_sources(uris)
# xsdata doesn't support output path
with _cd(SRC):
    transformer.process_classes()

# Fix bug in xsdata output
# https://github.com/tefra/xsdata/pull/806
light_source = next(PACKAGE_PATH.rglob("light_source.py"))
src = light_source.read_text()
src = src.replace("UnitsPower.M_W,", "UnitsPower.M_W_1,")
light_source.write_text(src)

black = ["black", str(PACKAGE_PATH), "-q", f"--line-length={LINE_LENGTH}"]
subprocess.check_call(black)  # noqa S

ruff = ["ruff", "-q", "--fix", str(PACKAGE_PATH)]
ruff.extend(f"--ignore={ignore}" for ignore in RUFF_IGNORE)
subprocess.check_call(ruff)  # noqa S

mypy = ["mypy", str(PACKAGE_PATH), "--strict"]
subprocess.check_output(mypy)  # noqa S

# print a bold green checkmark
print(f"\033[92m\033[1m✓ OME python model created at {PACKAGE}\033[0m")
