import os
from moto import mock_aws
from contextlib import contextmanager
import pytest
from dotenv import load_dotenv
from src.utils.storage import S3Storage
load_dotenv()


@contextmanager
def s3_storage(strategy):
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
def temp_storage(request, local_storage):
    backend, strategy, get_ruls = request.param
    if backend == "local":
        storage = local_storage
        storage.strategy = strategy
        yield storage, get_ruls
    elif backend == "s3":
        with s3_storage(strategy) as storage:
            yield storage, get_ruls
