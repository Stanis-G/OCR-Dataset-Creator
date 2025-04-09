import tempfile
import pytest
from utils.storage import LocalStorage


@pytest.fixture
def temp_local_storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(tmpdir, file_exists_strategy='rewrite')
        yield storage
