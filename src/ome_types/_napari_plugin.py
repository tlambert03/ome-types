from napari_plugin_engine import napari_hook_implementation

from .widgets import OMETree

METADATA_KEY = "ome_types"


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
