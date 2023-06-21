import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def cd(new_path: str | Path) -> Iterator[None]:
    prev = Path.cwd()
    os.chdir(Path(new_path).expanduser().absolute())
    try:
        yield
    finally:
        os.chdir(prev)


def resolve_source(source: str, recursive: bool) -> Iterator[str]:
    if "://" in source and not source.startswith("file://"):
        yield source
    else:
        path = Path(source).resolve()
        match = "**/*" if recursive else "*"
        if path.is_dir():
            for ext in ["wsdl", "xsd", "dtd", "xml", "json"]:
                yield from (x.as_uri() for x in path.glob(f"{match}.{ext}"))
        else:  # is file
            yield path.as_uri()
