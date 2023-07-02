import os
from pathlib import Path

import pytest

from ome_types import validate_xml

# to run this test locally, you can download QuPath.app as follows:
# python -m paquo get_qupath --install-path ./qupath/apps --download-path ./qupath/download 0.4.3  # noqa: E501
# (this is done automatically on CI)
if "PAQUO_QUPATH_DIR" not in os.environ:
    qupath_apps = Path(__file__).parent.parent / "qupath" / "apps"
    app_path = next(qupath_apps.glob("QuPath-*.app"), None)
    if app_path is not None:
        os.environ["PAQUO_QUPATH_DIR"] = str(app_path)

try:
    import shapely.geometry
    from paquo.hierarchy import QuPathPathObjectHierarchy
except (ValueError, ImportError):
    pytest.skip("Paquo not installed", allow_module_level=True)


@pytest.mark.filterwarnings("ignore:Importing submodules from ome_types.model")
def test_to_ome_xml() -> None:
    h = QuPathPathObjectHierarchy()
    h.add_annotation(roi=shapely.geometry.Point(1, 2))
    h.add_annotation(roi=shapely.geometry.LineString([(0, 0), (1, 1)]))
    h.add_annotation(roi=shapely.geometry.LinearRing([(0, 0), (1, 1), (2, 2)]))
    h.add_annotation(roi=shapely.geometry.box(0, 0, 1, 1))
    h.add_annotation(roi=shapely.geometry.Polygon([(0, 0), (1, 0), (2, 1), (0, 5)]))
    xml = h.to_ome_xml()
    validate_xml(xml)
