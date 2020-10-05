import pathlib

import pytest

TEST_FILES_DIR = (pathlib.Path(__file__).parent / "test_files").absolute()

CONTEXT = {
    "my_key": "name",
    "my_name": "James",
    "my_int": 10,
    "my": {"name": "David"},
    "obj": {"name": {"string": "David"}},
    "names": [{"name": "James"}, {"name": "David"}],
    "ints": [0, 1, 2, 3],
}


@pytest.fixture
def context():
    return CONTEXT
