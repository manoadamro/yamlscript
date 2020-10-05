import json
import pathlib
from typing import Any, Dict, Optional, Type, Union

import yaml

from . import globals, parser


def load(
    path: Union[pathlib.Path, str],
    context: Optional[Dict[str, Any]] = None,
    values: Optional[Dict[str, Any]] = None,
    g: Union[Dict[str, Any], Type[Any]] = globals.ExpressionGlobals,
    file_type: Optional[str] = None,
    parse: bool = True,
) -> Dict[str, Any]:
    path = pathlib.Path(path).absolute()
    if not path.is_file():
        raise Exception
    if file_type is None:
        parts = path.name.split(".")
        if len(parts) == 1:
            raise Exception
        file_type = parts[-1]
    if file_type == "json":
        content: Dict[str, Any] = json.loads(path.read_text())
    elif file_type in ("yaml", "yml"):
        content = yaml.safe_load(path.read_text())
    else:
        raise NotImplementedError
    if not parse:
        return content
    out: Dict[str, Any] = parser.sub(content, context, values, g)
    return out
