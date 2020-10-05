import fire
import pathlib
import json
from yamlscript import load
from typing import Dict, Any


def yamlscript(path: pathlib.Path, values: Dict[str, Any] = None, file_type: str = None, no_parse: bool = False):
    return json.dumps(load(path, context=values, file_type=file_type, parse=not no_parse))


def main():
    fire.Fire(yamlscript)
