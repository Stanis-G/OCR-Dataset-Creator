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
        storage_cls = S3Storage
        storage_params = {
            'dataset_name': 'test-bucket',
            'client_config': client_config,
            'file_exists_strategy': strategy,
        }
        yield storage_cls, storage_params


@pytest.fixture(params=[
    ("local", "rewrite", True),
    ("local", "skip", False),
    ("local", "raise", True),
    ("local", "invalid", False),
    ("s3", "rewrite", True),
    ("s3", "skip", False),
    ("s3", "raise", True),
    ("s3", "invalid", False),
])
def temp_storage(request, local_storage):
    backend, strategy, get_urls = request.param
    if backend == "local":
        storage_cls, storage_params = local_storage
        storage = storage_cls(**storage_params)
        storage.strategy = strategy
        yield storage, get_urls
    elif backend == "s3":
        with s3_storage(strategy) as storage_tpl:
            storage_cls, storage_params = storage_tpl
            storage = storage_cls(**storage_params)
            yield storage, get_urls
