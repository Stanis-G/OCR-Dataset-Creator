import pytest
import tempfile
from contextlib import contextmanager

from src.utils.storage import LocalStorage


@contextmanager
@pytest.fixture
def local_storage(strategy='rewrite'):
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_cls = LocalStorage
        storage_params = {'dataset_name': tmpdir, 'file_exists_strategy': strategy}
        yield storage_cls, storage_params
