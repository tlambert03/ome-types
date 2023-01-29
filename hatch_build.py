from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Custom Plugin."""

    PLUGIN_NAME = "ome_autogen"

    def initialize(self, version: str, build_data: dict) -> None:
        """Init before the build process begins."""
        import sys

        sys.path.append("src")

        import ome_autogen

        ome_autogen.convert_schema()
