from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from xsdata.codegen.transformer import SchemaTransformer

from ome_autogen import _util
from ome_autogen._config import OUTPUT_PACKAGE, get_config

DO_MYPY = os.environ.get("OME_AUTOGEN_MYPY", "0") == "1" or "--mypy" in sys.argv
SRC_PATH = Path(__file__).parent.parent
SCHEMA_FILE = SRC_PATH / "ome_types" / "ome-2016-06.xsd"
RUFF_IGNORE: list[str] = [
    "D101",  # Missing docstring in public class
    "D106",  # Missing docstring in public nested class
    "D205",  # 1 blank line required between summary line and description
    "D404",  # First word of the docstring should not be This
    "E501",  # Line too long
    "S105",  # Possible hardcoded password
]


def build_model(
    output_dir: Path | str = SRC_PATH,
    schema_file: Path | str = SCHEMA_FILE,
    line_length: int = 88,
    ruff_ignore: list[str] = RUFF_IGNORE,
    do_formatting: bool = True,
    do_mypy: bool = DO_MYPY,
) -> None:
    """Convert the OME schema to a python model."""
    config = get_config()
    transformer = SchemaTransformer(print=False, config=config)
    _print_gray(f"Processing {getattr(schema_file ,'name', schema_file)}...")
    transformer.process_sources([Path(schema_file).resolve().as_uri()])

    _print_gray("Writing Files...")
    # xsdata doesn't support output path
    with _util.cd(output_dir):
        transformer.process_classes()

    if not do_formatting and not do_mypy:
        _print_green(f"\u2713 OME python model created at {OUTPUT_PACKAGE}")
        return

    if do_formatting:
        _print_gray("Running black and ruff ...")

        package_dir = Path(output_dir) / OUTPUT_PACKAGE.replace(".", "/")
        black = ["black", str(package_dir), "-q", f"--line-length={line_length}"]
        subprocess.check_call(black)  # noqa S

        ruff = ["ruff", "-q", "--fix", str(package_dir)]
        ruff.extend(f"--ignore={ignore}" for ignore in ruff_ignore)
        subprocess.check_call(ruff)  # noqa S

    if do_mypy:
        _print_gray("Running mypy ...")

        mypy = ["mypy", str(package_dir), "--strict"]
        subprocess.check_output(mypy)  # noqa S

    # print a bold green checkmark
    _print_green(f"\u2713 OME python model created at {OUTPUT_PACKAGE}")


def _print_gray(text: str) -> None:
    print(f"\033[90m\033[1m{text}\033[0m")


def _print_green(text: str) -> None:
    print(f"\033[92m\033[1m{text}\033[0m")
