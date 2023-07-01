from __future__ import annotations

import hashlib
import pathlib
import shutil
import sys
import tempfile
import urllib.request
from typing import TYPE_CHECKING, Iterator, cast

import pytest

# pytest.skip("Skipping paquo tests", allow_module_level=True)
import shapely.geometry
from paquo.projects import QuPathProject

if TYPE_CHECKING:
    from paquo.hierarchy import QuPathPathObjectHierarchy
    from paquo.images import QuPathProjectImageEntry


def md5(fn):
    if sys.version_info >= (3, 9):
        m = hashlib.md5(usedforsecurity=False)
    else:
        m = hashlib.md5()  # nosec B324
    with open(fn, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            m.update(chunk)
    return m.hexdigest()


@pytest.fixture(scope="session")
def svs_small():
    """download the smallest aperio test image svs"""
    IMAGES_BASE_URL = "http://openslide.cs.cmu.edu/download/openslide-testdata/Aperio/"

    small_image = "CMU-1-Small-Region.svs"
    small_image_md5 = "1ad6e35c9d17e4d85fb7e3143b328efe"
    data_dir = pathlib.Path(__file__).parent / "data"

    data_dir.mkdir(parents=True, exist_ok=True)
    img_fn = data_dir / small_image

    if not img_fn.is_file():
        # download svs from openslide test images
        url = IMAGES_BASE_URL + small_image
        with urllib.request.urlopen(url) as response, open(
            img_fn, "wb"
        ) as out_file:  # nosec B310
            shutil.copyfileobj(response, out_file)

    if md5(img_fn) != small_image_md5:  # pragma: no cover
        shutil.rmtree(img_fn)
        pytest.fail("incorrect md5")
    else:
        yield img_fn.absolute()


@pytest.fixture(scope="module")
def project_and_changes(svs_small) -> Iterator[tuple[pathlib.Path, dict]]:
    with tempfile.TemporaryDirectory(prefix="paquo-") as tmpdir:
        qp = QuPathProject(tmpdir, mode="x")
        entry = cast("QuPathProjectImageEntry", qp.add_image(svs_small))
        entry.hierarchy.add_annotation(roi=shapely.geometry.Point(1, 2))
        qp.save()
        project_path = qp.path.parent
        del qp

        last_changes = {}
        for file in project_path.glob("**/*.*"):
            p = str(file.absolute())
            last_changes[p] = file.stat().st_mtime

        yield project_path, last_changes


@pytest.fixture
def readonly_project(project_and_changes: tuple[pathlib.Path, dict]) -> QuPathProject:
    project_path, changes = project_and_changes
    qp = QuPathProject(project_path, mode="r")
    qp.__changes = changes  # type: ignore
    return qp


def test_hierarchy(readonly_project: QuPathProject):
    image = readonly_project.images[0]
    hierarchy = cast("QuPathPathObjectHierarchy", image.hierarchy)
    hierarchy.to_ome_xml()
    breakpoint()
