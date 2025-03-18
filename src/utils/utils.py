import os
from io import BytesIO
import boto3
from botocore.exceptions import ConnectionClosedError, ClientError
from dotenv import load_dotenv
from PIL import Image
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

load_dotenv()
MINIO_URL = os.getenv("MINIO_URL")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")


def set_driver(driver_path, download_dir=None):
    
    options = Options()
    if download_dir:
        options = webdriver.ChromeOptions()
        prefs = {
            "profile.default_content_settings.popups": 0,
            "download.default_directory": os.path.abspath(download_dir),
            "directory_upgrade": True,
        }
        options.add_experimental_option("prefs", prefs)
    options.add_argument("--headless") # Run in headless mode
    service = Service(driver_path)
    driver = webdriver.Chrome(options=options, service=service)
    return driver


def get_s3_client(bucket_name='ocr-dataset', retries=10, delay=1):
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url=MINIO_URL,
        aws_access_key_id=MINIO_ROOT_USER,
        aws_secret_access_key=MINIO_ROOT_PASSWORD,
    )

    # Create bucket if it doesn't exist
    try:
        for i in range(retries):
            try:
                s3.head_bucket(Bucket=bucket_name)
                continue
            except ConnectionClosedError:
                if i < retries - 1:
                    time.sleep(delay)
                else:
                    raise
    except s3.exceptions.ClientError:
        s3.create_bucket(Bucket=bucket_name)

    return s3


def save_file_to_s3(file_path, file_name, bucket_name, prefix):
    s3 = get_s3_client(bucket_name)
    file_ref = f'{prefix}/{file_name}' if prefix else file_name
    s3.upload_file(file_path, bucket_name, file_ref)


def save_fileobj_to_s3(content, file_name, bucket_name, prefix=None):
    if isinstance(content, str):
        file_obj = BytesIO(content.encode("utf-8"))
    elif isinstance(content, Image.Image):
        file_obj = BytesIO()
        content.save(file_obj, format='PNG')
        file_obj.seek(0)
    s3 = get_s3_client(bucket_name)
    file_ref = f'{prefix}/{file_name}' if prefix else file_name
    s3.upload_fileobj(file_obj, bucket_name, file_ref)


def get_s3_url(bucket_name, file_name, expiration=30):
    s3 = get_s3_client(bucket_name)
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": file_name},
        ExpiresIn=expiration,
    )
    return url


def read_file_from_s3(file_name, bucket_name):
    s3 = get_s3_client(bucket_name)
    response = s3.get_object(Bucket=bucket_name, Key=file_name)

    # Read data
    file_data = response['Body'].read()

    if file_name.startswith('texts') or file_name.startswith('pages'):
        # Convert bytes to string (if text file)
        return file_data.decode("utf-8")
    elif file_name.startswith('images'):
        # Open image using PIL
        file_data = BytesIO(file_data)
        return Image.open(file_data)


def list_objects_in_bucket(bucket_name, prefix, page_size=1000):
    s3 = get_s3_client(bucket_name)
    objects = []
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix, PaginationConfig={'PageSize': page_size}):
        objects.extend(obj["Key"] for obj in page.get("Contents", []))

    return objects


def check_s3_file_exists(bucket_name, file_name):
    s3 = get_s3_client(bucket_name)
    try:
        s3.head_object(Bucket=bucket_name, Key=file_name)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False # File does not exist
        raise # Raise other errors
