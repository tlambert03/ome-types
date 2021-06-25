import warnings
from typing import Union

from napari_plugin_engine import napari_hook_implementation
from qtpy.QtCore import QMimeData, Qt
from qtpy.QtWidgets import QTreeWidget, QTreeWidgetItem

from ome_types import OME


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return OMETree, {"name": "OME Metadata Viewer"}


@napari_hook_implementation
def napari_get_reader(path):
    """Show OME XML if an ome.xml file is dropped on the viewer."""
    if isinstance(path, str) and path.endswith("ome.xml"):
        return view_ome_xml


def view_ome_xml(path):
    from napari._qt.qt_main_window import _QtMainWindow

    # close your eyes, or look away...
    # there is nothing worth looking at here!
    window = _QtMainWindow.current()
    if not window:
        return
    viewer = window.qt_viewer.viewer
    dw, widget = viewer.window.add_plugin_dock_widget("ome-types")
    widget.update(path)

    return [(None,)]  # sentinel


class OMETree(QTreeWidget):
    """A Widget that can show OME XML"""

    def __init__(self, ome_dict: dict = None, parent=None) -> None:
        super().__init__(parent=parent)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setHeaderHidden(True)
        self.update(ome_dict)

    def update(self, ome: Union[OME, str]):
        if not ome:
            return
        if isinstance(ome, str):
            try:
                if ome.endswith(".xml"):
                    ome = OME.from_xml(ome)
                elif ome.lower().endswith((".tif", ".tiff")):
                    ome = OME.from_tiff(ome)
                else:
                    warnings.warn(f"Unrecognized file type: {ome}")
                    return
            except Exception as e:
                warnings.warn(f"Could not parse OME metadata from {ome}: {e}")
                return

        self._fill_item(ome.dict(exclude_unset=True))

    def _fill_item(self, obj, item: QTreeWidgetItem = None):
        if item is None:
            self.clear()
            item = self.invisibleRootItem()
        if isinstance(obj, dict):
            for key, val in sorted(obj.items()):
                child = QTreeWidgetItem([key])
                item.addChild(child)
                self._fill_item(val, child)
        elif isinstance(obj, (list, tuple)):
            for n, val in enumerate(obj):
                text = val.get("id", n) if hasattr(val, "get") else n
                child = QTreeWidgetItem([str(text)])
                item.addChild(child)
                self._fill_item(val, child)
        else:
            t = getattr(obj, "value", str(obj))
            item.setText(0, f"{item.text(0)}: {t}")

    def dropMimeData(
        self, parent: QTreeWidgetItem, index: int, data: QMimeData, a
    ) -> bool:
        if data.hasUrls():
            for url in data.urls():
                lf = url.toLocalFile()
                if lf.endswith((".xml", ".tiff", ".tif")):
                    self.update(lf)
                    return True
        return False

    def mimeTypes(self):
        return ["text/uri-list"]

    def supportedDropActions(self):
        return Qt.CopyAction


if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication

    app = QApplication([])

    widget = OMETree()
    widget.show()

    app.exec()
