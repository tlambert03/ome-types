import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def _cd(new_path: str | Path) -> Iterator[None]:
    prev = Path.cwd()
    os.chdir(Path(new_path).expanduser().absolute())
    try:
        yield
    finally:
        os.chdir(prev)
