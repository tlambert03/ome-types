import subprocess
from pathlib import Path

from xsdata.codegen.transformer import SchemaTransformer
from xsdata.logger import logger

from ome_autogen import _util

from ._config import OUTPUT_PACKAGE, get_config

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
logger.setLevel("DEBUG")


def convert_schema(
    output_dir: Path | str = SRC_PATH,
    schema_file: Path | str = SCHEMA_FILE,
    line_length: int = 88,
    ruff_ignore: list[str] = RUFF_IGNORE,
    do_linting: bool = True,
) -> None:
    """Convert the OME schema to a python model."""
    config = get_config()
    transformer = SchemaTransformer(print=False, config=config)
    transformer.process_sources([Path(schema_file).resolve().as_uri()])

    plurals = _util.get_plural_names(schema=schema_file)

    # pluralize field names:
    for clazz in transformer.classes:
        for attr in clazz.attrs:
            if attr.is_list:
                # XXX: should we be adding s?
                attr.name = plurals.get(attr.name, f"{attr.name}")

    # xsdata doesn't support output path
    with _util.cd(output_dir):
        transformer.process_classes()

    if not do_linting:
        print(f"\033[92m\033[1m✓ OME python model created at {OUTPUT_PACKAGE}\033[0m")
        return

    package_dir = Path(output_dir) / OUTPUT_PACKAGE.replace(".", "/")
    black = ["black", str(package_dir), "-q", f"--line-length={line_length}"]
    subprocess.check_call(black)  # noqa S

    ruff = ["ruff", "-q", "--fix", str(package_dir)]
    ruff.extend(f"--ignore={ignore}" for ignore in ruff_ignore)
    subprocess.check_call(ruff)  # noqa S

    mypy = ["mypy", str(package_dir), "--strict"]
    subprocess.check_output(mypy)  # noqa S

    # print a bold green checkmark
    print(f"\033[92m\033[1m✓ OME python model created at {OUTPUT_PACKAGE}\033[0m")
