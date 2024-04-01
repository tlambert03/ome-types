import os
import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Custom Plugin."""

    PLUGIN_NAME = "some_autogen"

    def initialize(self, version: str, build_data: dict) -> None:
        """Init before the build process begins."""
        if os.getenv("SKIP_AUTOGEN"):
            return

        sys.path.append("src")

        import some_autogen.main

        some_autogen.main.build_model(do_mypy=False)
