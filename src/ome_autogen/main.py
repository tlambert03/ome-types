from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from shutil import rmtree
from typing import Any

from ome_autogen import _util
from ome_autogen._config import get_config
from ome_autogen._transformer import OMETransformer
from ome_types import model
from ome_types._mixins._base_type import OMEType

BLACK_LINE_LENGTH = 88
BLACK_TARGET_VERSION = "py37"
BLACK_SKIP_TRAILING_COMMA = False  # use trailing commas as a reason to split lines?
OUTPUT_PACKAGE = "ome_types._autogenerated.ome_2016_06"
DO_MYPY = os.environ.get("OME_AUTOGEN_MYPY", "0") == "1" or "--mypy" in sys.argv
SRC_PATH = Path(__file__).parent.parent
SCHEMA_FILE = (SRC_PATH / "ome_types" / "ome-2016-06.xsd").absolute()
RUFF_IGNORE: list[str] = [
    "D101",  # Missing docstring in public class
    "D106",  # Missing docstring in public nested class
    "D205",  # 1 blank line required between summary line and description
    "D404",  # First word of the docstring should not be This
    "E501",  # Line too long
    "S105",  # Possible hardcoded password
    "RUF002",  # ambiguous-unicode-character-docstring
]


def build_model(
    output_dir: Path | str = SRC_PATH,
    schema_file: Path | str = SCHEMA_FILE,
    target_package: str = OUTPUT_PACKAGE,
    ruff_ignore: list[str] = RUFF_IGNORE,
    do_formatting: bool = True,
    do_mypy: bool = DO_MYPY,
) -> None:
    """Convert the OME schema to a python model."""
    config = get_config(target_package)
    transformer = OMETransformer(print=False, config=config)

    _print_gray(f"Processing {getattr(schema_file ,'name', schema_file)}...")
    transformer.process_sources([Path(schema_file).resolve().as_uri()])

    package_dir = str(Path(output_dir) / OUTPUT_PACKAGE.replace(".", "/"))
    rmtree(package_dir, ignore_errors=True)
    with _util.cd(output_dir):  # xsdata doesn't support output path
        _print_gray("Writing Files...")
        transformer.process_classes()

    _build_typed_dicts(package_dir)
    if do_formatting:
        _fix_formatting(package_dir, ruff_ignore)

    if do_mypy:
        _check_mypy(package_dir)

    _print_green(f"OME python model created at {OUTPUT_PACKAGE}")


def _fix_formatting(package_dir: str, ruff_ignore: list[str] = RUFF_IGNORE) -> None:
    _print_gray("Running black and ruff ...")

    ruff = ["ruff", "-q", "--fix", package_dir]
    ruff.extend(f"--ignore={ignore}" for ignore in ruff_ignore)
    subprocess.check_call(ruff)  # noqa S

    black = [
        "black",
        "-q",
        f"--line-length={BLACK_LINE_LENGTH}",
        f"--target-version={BLACK_TARGET_VERSION}",
    ]
    if BLACK_SKIP_TRAILING_COMMA:  # pragma: no cover
        black.append("--skip-magic-trailing-comma")
    black.extend([str(x) for x in Path(package_dir).rglob("*.py")])
    subprocess.check_call(black)  # noqa S


def _check_mypy(package_dir: str) -> None:
    _print_gray("Running mypy ...")

    mypy = ["mypy", package_dir, "--strict"]
    try:
        subprocess.check_output(mypy, stderr=subprocess.STDOUT)  # noqa S
    except subprocess.CalledProcessError as e:  # pragma: no cover
        raise RuntimeError(f"mypy errors:\n\n{e.output.decode()}") from e


def _print_gray(text: str) -> None:
    if os.name != "nt":
        # UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'
        text = f"\033[90m\033[1m{text}\033[0m"
    print(text)


def _print_green(text: str) -> None:
    if os.name != "nt":
        # UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'
        text = f"\033[92m\033[1m{text}\033[0m"
    print(text)


KWARGS_MODULE = """
from __future__ import annotations
from typing_extensions import TypedDict, TypeAlias
from typing import Union, List
from datetime import datetime
import ome_types.model as ome

class RefDict(TypedDict):
    id: str
"""


def _build_typed_dicts(package_dir: str) -> None:
    """Create a TypedDict class for each OMEType subclass.

    Useful for passing kwargs to the constructors.

    def foo(**kwargs: Unpack[ome.ImageDict]) -> None:
        ...
    """
    # sourcery skip: assign-if-exp, reintroduce-else
    try:
        from pydantic._internal._repr import display_as_type
    except ImportError:
        from pydantic.typing import display_as_type  # type: ignore

    ome_models = {
        name: obj
        for name, obj in vars(model).items()
        if isinstance(obj, type) and issubclass(obj, OMEType) and obj.__annotations__
    }

    def _disp_type(obj: Any) -> str:
        x = display_as_type(obj).replace("NoneType", "None")
        if "ForwardRef" in x:
            #  replace "List[ForwardRef('Map.M')]" with "List[Map.M]"
            x = re.sub(r"ForwardRef\('([a-zA-Z_.]*)'\)", r"\1", x)
        x = re.sub("ome_types\._autogenerated\.ome_2016_06.[^.]+.", "", x)
        return x

    # add TypedDicts for all models
    module = KWARGS_MODULE
    SUFFIX = "Dict"
    CLASS = "class {name}(TypedDict, total=False):\n\t{fields}\n\n"
    for cls_name, m in sorted(ome_models.items()):
        if cls_name.endswith("Ref"):
            module += f"{cls_name}: TypeAlias = RefDict\n"
        else:
            _fields = [
                f"{k}: {_disp_type(v.annotation)}"
                for k, v in sorted(m.model_fields.items())
            ]
            if _fields:
                module += CLASS.format(
                    name=f"{m.__name__}{SUFFIX}", fields="\n\t".join(_fields)
                )
            else:
                module += (
                    f"class {m.__name__}{SUFFIX}(TypedDict, total=False):\n\tpass\n\n"
                )

    # fix name spaces
    # prefix all remaining capitalized words with ome.
    def _repl(match: re.Match) -> str:
        word = match[1]
        if word in {"None", "True", "False", "Union", "List", "TypedDict", "TypeAlias"}:
            return word
        if word.endswith(SUFFIX):
            return word
        if word in ome_models:
            return word + SUFFIX
        # the rest are enums, they can be passed as strings
        return f"ome.{word} | str"

    module = re.sub(r"\b([A-Z][a-zA-Z_^.]*)\b", _repl, module)
    (Path(package_dir) / "kwargs.py").write_text(module)
