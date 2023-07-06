import os
import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Custom Plugin."""

    PLUGIN_NAME = "ome_autogen"

    def initialize(self, version: str, build_data: dict) -> None:
        """Init before the build process begins."""
        if os.getenv("SKIP_AUTOGEN"):
            return

        sys.path.append("src")

        import ome_autogen.main

        ome_autogen.main.build_model(do_mypy=False)
