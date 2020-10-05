import json
import pathlib

import pytest

from yamlscript import load

from .conftest import TEST_FILES_DIR

EXPECTED = {
    "enum": {"James": 10, "David": 11},
    "list": ["James", "David"],
    "name": "James",
}
UNPARSED = json.loads((TEST_FILES_DIR / "json_format.json").read_text())


@pytest.mark.parametrize(
    "path,kwargs,expected",
    [
        (TEST_FILES_DIR / "json_format.json", {}, EXPECTED),
        (TEST_FILES_DIR / "json_format.json", {"parse": False}, UNPARSED),
        (TEST_FILES_DIR / "yaml_format.yaml", {}, EXPECTED),
        (TEST_FILES_DIR / "yaml_format.yaml", {"parse": False}, UNPARSED),
        (TEST_FILES_DIR / "yaml_format.yml", {}, EXPECTED),
        (TEST_FILES_DIR / "yaml_format.yml", {"parse": False}, UNPARSED),
        (TEST_FILES_DIR / "anonymous_format", {"file_type": "yaml"}, EXPECTED),
        (
            TEST_FILES_DIR / "anonymous_format",
            {"file_type": "yaml", "parse": False},
            UNPARSED,
        ),
        (
            TEST_FILES_DIR / "anonymous_format",
            {"file_type": "nope"},
            NotImplementedError,
        ),
        (TEST_FILES_DIR / "anonymous_format", {}, Exception),
        (TEST_FILES_DIR, {}, Exception),
    ],
)
def test_load(path, kwargs, expected, context):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            load(path=path, **kwargs, context=context)
    else:
        output = load(path=path, **kwargs, context=context)
        assert output == expected
