import pytest
import tempfile
from contextlib import contextmanager

from utils.storage import LocalStorage


@contextmanager
@pytest.fixture
def local_storage(strategy='rewrite'):
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(tmpdir, file_exists_strategy=strategy)
        yield storage
