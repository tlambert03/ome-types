import os
import subprocess
from pathlib import Path

from xsdata.formats.dataclass.parsers import XmlParser

os.chdir(Path(__file__).parent)

subprocess.run(["xsdata", "schema.xsd"])
# subprocess.run(["black", "generated"])
# subprocess.run(["ruff", "generated", "--fix", "--ignore=D1"])

from generated.schema_mod import Root  # noqa: E402

result = XmlParser().parse("instance.xml", Root)
print(result)
