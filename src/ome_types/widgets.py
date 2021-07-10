import os
import warnings
from typing import TYPE_CHECKING, Optional, Union

from .model import OME

try:
    from qtpy.QtCore import QMimeData, Qt
    from qtpy.QtWidgets import QTreeWidget, QTreeWidgetItem
except ImportError:
    raise ImportError(
        "qtpy and a Qt backend (pyside or pyqt) is required to use the OME widget:\n"
        "pip install qtpy pyqt5"
    )


if TYPE_CHECKING:
    import napari


class OMETree(QTreeWidget):
    """A Widget that can show OME XML"""

    def __init__(
        self, ome_dict: dict = None, viewer: "napari.viewer.Viewer" = None, parent=None
    ) -> None:
        super().__init__(parent=parent)
        self._viewer = viewer
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setIndentation(15)

        item = self.headerItem()
        font = item.font(0)
        font.setBold(True)
        item.setFont(0, font)
        self.clear()

        self._current_path: Optional[str] = None
        if ome_dict:
            self.update(ome_dict)

        if viewer is not None:
            viewer.layers.selection.events.active.connect(
                lambda e: self._try_load_layer(e.value)
            )
            self._try_load_layer(viewer.layers.selection.active)

    def clear(self):
        self.headerItem().setText(0, "drag/drop file...")
        super().clear()

    def _try_load_layer(self, layer: "napari.layers.Layer"):
        """Handle napari viewer behavior"""
        from ._napari_plugin import METADATA_KEY

        if layer is not None:
            path = str(layer.source.path)

            # deprecated... don't do this ... it should be a dict
            if callable(layer.metadata):
                ome_meta = layer.metadata()
            elif isinstance(layer.metadata, OME):
                ome_meta = layer.metadata
            else:
                ome_meta = layer.metadata.get(METADATA_KEY)
                if callable(ome_meta):
                    ome_meta = ome_meta()

            ome = None
            if isinstance(ome_meta, OME):
                ome = ome_meta
            elif path.endswith((".tiff", ".tif")) and path != self._current_path:
                try:
                    ome = OME.from_tiff(path)
                except Exception:
                    return
            if isinstance(ome, OME):
                self._current_path = path
                self.update(ome)
                self.headerItem().setText(0, os.path.basename(path))
        else:
            self._current_path = None
            self.clear()

    def update(self, ome: Union[OME, str]):
        if not ome:
            return
        if isinstance(ome, OME):
            _ome = ome
        elif isinstance(ome, str):
            if ome == self._current_path:
                return
            try:
                if ome.endswith(".xml"):
                    _ome = OME.from_xml(ome)
                elif ome.lower().endswith((".tif", ".tiff")):
                    _ome = OME.from_tiff(ome)
                else:
                    warnings.warn(f"Unrecognized file type: {ome}")
                    return
            except Exception as e:
                warnings.warn(f"Could not parse OME metadata from {ome}: {e}")
                return
            self.headerItem().setText(0, os.path.basename(ome))
            self._current_path = ome
        else:
            raise TypeError("must be OME object or string")
        self._fill_item(_ome.dict(exclude_unset=True))

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
