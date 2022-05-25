import inspect
from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel
from sphinx.application import Sphinx
from sphinx.ext.autodoc import Options


def process_signature(
    app: Sphinx,
    what: str,
    name: str,
    obj: Any,
    options: Options,
    signature: str,
    return_annotation: str,
) -> Optional[Tuple[str, None]]:
    # just use names for pydantic signatures.  Type hints will be in params
    if isinstance(obj, type) and issubclass(obj, BaseModel):
        s = inspect.signature(obj)
        s = s.replace(
            parameters=[p.replace(annotation=p.empty) for p in s.parameters.values()]
        )
        return (str(s), None)
    return None


def setup(app: Sphinx) -> Dict[str, bool]:
    app.add_config_value("always_document_param_types", False, "html")
    app.add_config_value("typehints_fully_qualified", False, "env")
    app.add_config_value("typehints_document_rtype", True, "env")
    app.add_config_value("typehints_use_rtype", True, "env")
    app.add_config_value("typehints_defaults", None, "env")
    app.add_config_value("simplify_optional_unions", True, "env")
    app.add_config_value("typehints_formatter", None, "env")
    app.connect("autodoc-process-signature", process_signature)
    return {"parallel_read_safe": True}
