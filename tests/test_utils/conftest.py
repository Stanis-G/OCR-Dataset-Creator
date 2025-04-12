import os
import tempfile
from moto import mock_aws
from contextlib import contextmanager
import pytest
from dotenv import load_dotenv
from utils.storage import LocalStorage, S3Storage
load_dotenv()


@contextmanager
def local_storage_fixture(strategy):
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(tmpdir, file_exists_strategy=strategy)
        yield storage

@contextmanager
def s3_storage_fixture(strategy):
    client_config = dict(
        endpoint_url=os.getenv("MINIO_URL"),
        aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
        aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
    )
    with mock_aws():
        storage = S3Storage('test-bucket', client_config, file_exists_strategy=strategy)
        yield storage


@pytest.fixture(params=[
    ("local", "rewrite"),
    ("local", "skip"),
    ("local", "raise"),
    ("local", "invalid"),
    ("s3", "rewrite"),
    ("s3", "skip"),
    ("s3", "raise"),
    ("s3", "invalid"),
])
def temp_storage(request):
    backend, strategy = request.param
    if backend == "local":
        with local_storage_fixture(strategy) as storage:
            yield storage
    elif backend == "s3":
        with s3_storage_fixture(strategy) as storage:
            yield storage
