from distutils.command.build_py import build_py as _build_py
from runpy import run_path

from setuptools import setup


class build_py(_build_py):
    run_path("src/ome_autogen.py", run_name="__main__")


setup(
    cmdclass={"build_py": build_py},
    use_scm_version={"write_to": "src/ome_types/_version.py"},
)
