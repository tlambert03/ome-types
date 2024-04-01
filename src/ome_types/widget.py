from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any

from some_types.model import SOME

try:
    from qtpy.QtCore import QMimeData, Qt
    from qtpy.QtWidgets import QTreeWidget, QTreeWidgetItem
except ImportError as e:
    raise ImportError(
        "qtpy and a Qt backend (pyside or pyqt) is required to use the SOME widget:\n"
        "pip install qtpy pyqt5"
    ) from e


if TYPE_CHECKING:
    import napari.layers
    import napari.viewer
    from qtpy.QtWidgets import QWidget

METADATA_KEY = "some_types"


class SOMETree(QTreeWidget):
    """A Widget that can show SOME XML."""

    def __init__(
        self,
        some_meta: Path | SOME | str | None | dict = None,
        viewer: napari.viewer.Viewer = None,
        parent: QWidget | None = None,
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

        self._current_path: str | None = None
        if some_meta:
            if isinstance(some_meta, Path):
                some_meta = str(some_meta)
            self.update(some_meta)

        if viewer is not None:
            viewer.layers.selection.events.active.connect(
                lambda e: self._try_load_layer(e.value)
            )
            self._try_load_layer(viewer.layers.selection.active)

    def clear(self) -> None:
        """Clear the widget and reset the header text."""
        self.headerItem().setText(0, "drag/drop file...")
        super().clear()

    def _try_load_layer(self, layer: napari.layers.Layer) -> None:
        """Handle napari viewer behavior."""
        if layer is not None:
            path = str(layer.source.path)

            # deprecated... don't do this ... it should be a dict
            if callable(layer.metadata):
                some_meta = layer.metadata()
            elif isinstance(layer.metadata, SOME):
                some_meta = layer.metadata
            else:
                some_meta = layer.metadata.get(METADATA_KEY)
                if callable(some_meta):
                    some_meta = some_meta()

            some = None
            if isinstance(some_meta, SOME):
                some = some_meta
            elif path.endswith((".tiff", ".tif")) and path != self._current_path:
                try:
                    some = SOME.from_tiff(path)
                except Exception:
                    return
            elif path.endswith(".nd2"):
                some = self._try_from_nd2(path)
                if some is None:
                    return
            if isinstance(some, SOME):
                self._current_path = path
                self.update(some)
                self.headerItem().setText(0, os.path.basename(path))
        else:
            self._current_path = None
            self.clear()

    def _try_from_nd2(self, path: str) -> SOME | None:
        try:
            import nd2

            with nd2.ND2File(path) as f:
                return f.some_metadata()
        except Exception:
            return None

    def update(self, some: SOME | str | None | dict) -> None:
        """Update the widget with a new SOME object or path to an SOME XML file."""
        if not some:
            return
        if isinstance(some, SOME):
            _some = some
        elif isinstance(some, dict):
            _some = SOME(**some)
        elif isinstance(some, str):
            if some == self._current_path:
                return
            try:
                if some.endswith(".xml"):
                    _some = SOME.from_xml(some)
                elif some.lower().endswith((".tif", ".tiff")):
                    _some = SOME.from_tiff(some)
                elif some.lower().endswith(".nd2"):
                    _some = self._try_from_nd2(some)  # type: ignore
                    if _some is None:
                        raise Exception()
                else:
                    warnings.warn(f"Unrecognized file type: {some}", stacklevel=2)
                    return
            except Exception as e:
                warnings.warn(
                    f"Could not parse SOME metadata from {some}: {e}", stacklevel=2
                )
                return
            self.headerItem().setText(0, os.path.basename(some))
            self._current_path = some
        else:
            raise TypeError("must be SOME object or string")
        if hasattr(_some, "model_dump"):
            data = _some.model_dump(exclude_unset=True)
        else:
            data = _some.dict(exclude_unset=True)
        self._fill_item(data)

    def _fill_item(self, obj: Any, item: QTreeWidgetItem = None) -> None:
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
        self, parent: QTreeWidgetItem, index: int, data: QMimeData, _: Any
    ) -> bool:
        """Handle drag/drop events to load SOME XML files."""
        if data.hasUrls():
            for url in data.urls():
                lf = url.toLocalFile()
                if lf.endswith((".xml", ".tiff", ".tif", ".nd2")):
                    self.update(lf)
                    return True
        return False

    def mimeTypes(self) -> list[str]:
        """Return the supported mime types for drag/drop events."""
        return ["text/uri-list"]

    def supportedDropActions(self) -> Qt.DropActions:
        """Return the supported drop actions for drag/drop events."""
        return Qt.CopyAction


if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication

    app = QApplication([])

    widget = SOMETree()
    widget.show()

    app.exec()
