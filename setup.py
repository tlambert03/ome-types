import sys

sys.stderr.write(
    """
===============================
Unsupported installation method
===============================
ome-types does not support installation with `python setup.py install`.
Please use `python -m pip install .` instead.
"""
)
sys.exit(1)


# The below code will never execute, however GitHub is particularly
# picky about where it finds Python packaging metadata.
# See: https://github.com/github/feedback/discussions/6456
#
# To be removed once GitHub catches up.

setup(  # type: ignore  # noqa
    name="ome-types",
    install_requires=[
        "Pint >=0.15",
        "lxml >=4.8.0",
        "pydantic[email] >=1.0",
        "xmlschema >=1.4.1",
    ],
)
