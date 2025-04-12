from abc import ABC, abstractmethod
import os
from io import BytesIO
import boto3
from botocore.config import Config
from botocore.exceptions import ConnectionClosedError, ClientError
from PIL import Image
import time


class Storage(ABC):

    def __init__(self, file_exists_strategy='skip'):
        self.strategy = file_exists_strategy


    @abstractmethod
    def check_file_exists(self, *args, **kwargs):
        pass
    

    def _file_exists_handler(self, file_name, subdir):
        """Returns True if save_file method in subclasses should be executed"""
        file_exists = self.check_file_exists(file_name, subdir)
        if file_exists:
            if self.strategy == 'skip':
                return False 
            elif self.strategy == 'rewrite':
                return True
            elif self.strategy == 'raise':
                raise FileExistsError(f'File "{file_name}" already exists in subdir "{subdir}"')
            else:
                raise ValueError(f'"strategy" should be one of the "skip", "rewrite", "raise", got "{self.strategy}"')
        return True


class LocalStorage(Storage):
    
    def __init__(self, dataset_name, file_exists_strategy='skip'):
        super().__init__(file_exists_strategy=file_exists_strategy)
        self.data_dir = dataset_name


    def save_file(self, content, file_name, subdir):
        # Decide whether file should be saved
        if self._file_exists_handler(file_name, subdir):
            
            # Create subdir if it doesn't exist
            subdir_path = os.path.join(self.data_dir, subdir)
            os.makedirs(subdir_path, exist_ok=True)

            file_name_full = os.path.join(subdir_path, file_name)
            if isinstance(content, str):
                with open(file_name_full, 'w', encoding='utf-8') as f:
                    f.write(content)
            elif isinstance(content, Image.Image):
                content.save(file_name_full, format='PNG')
            else:
                raise TypeError('Content should be one of the types: str, ImageImage')


    def read_file(self, file_name, subdir, file_type='text'):
        file_name_full = os.path.join(self.data_dir, subdir, file_name)
        if file_type == 'text':
            with open(file_name_full, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        elif file_type == 'image':
            return Image.open(file_name_full, mode='r')
        else:
            raise ValueError('Only "text" or "image" file type is supported')
        

    def read_all(self, subdir):
        """Get list of filenames in the specified path"""
        full_path = os.path.join(self.data_dir, subdir)
        return os.listdir(full_path)
    

    def check_file_exists(self, file_name, subdir):
        file_name_full = os.path.join(self.data_dir, subdir, file_name)
        return os.path.exists(file_name_full)
    

    def delete_file(self, file_name, subdir):
        if self.check_file_exists(file_name, subdir):
            file_name_full = os.path.join(self.data_dir, subdir, file_name)
            os.remove(file_name_full)


class S3Storage(Storage):
    
    def __init__(self, dataset_name, client_config, file_exists_strategy='skip'):
        super().__init__(file_exists_strategy=file_exists_strategy)
        self.bucket_name = dataset_name
        self._get_s3_client(client_config)


    def _get_s3_client(self, client_config, retries=10, delay=1):
        """Create s3 client"""
        client_config.update(
            dict(
                service_name='s3',
                config=Config(retries={'max_attempts': retries, 'mode': 'standard'}),
            )
        )
        session = boto3.session.Session()
        s3 = session.client(**client_config)

        # Create bucket if it doesn't exist
        try:
            for i in range(retries):
                try:
                    s3.head_bucket(Bucket=self.bucket_name)
                    continue
                except ConnectionClosedError:
                    if i < retries - 1:
                        time.sleep(delay * (2 ** i)) # Exponential backoff
                    else:
                        raise
        except s3.exceptions.ClientError:
            s3.create_bucket(Bucket=self.bucket_name)

        self.s3 = s3
    

    def save_file(self, content, file_name, subdir):
        # Decide whether file should be saved
        if self._file_exists_handler(file_name, subdir):
            if isinstance(content, str):
                file_obj = BytesIO(content.encode("utf-8"))
            elif isinstance(content, Image.Image):
                file_obj = BytesIO()
                content.save(file_obj, format='PNG')
                file_obj.seek(0)
            else:
                raise TypeError('Content should be one of the types: str, ImageImage')
            file_name_full = f'{subdir}/{file_name}'
            self.s3.upload_fileobj(file_obj, self.bucket_name, file_name_full)


    def read_file(self, file_name, subdir, file_type='text'):
        """Get file by name"""

        # Read file
        file_name_full = f'{subdir}/{file_name}' if not file_name.startswith(subdir) else file_name
        response = self.s3.get_object(Bucket=self.bucket_name, Key=file_name_full)
        file_data = response['Body'].read()

        # Process data
        if file_type == 'text':
            # Convert bytes to string (if text file)
            return file_data.decode("utf-8")
        elif file_type == 'image':
            # Open image using PIL
            file_data = BytesIO(file_data)
            return Image.open(file_data)
        else:
            raise ValueError('Only "text" or "image" file type is supported')
        

    def read_all(self, subdir, page_size=1000):    
        """Get list of object names with the specified prefix"""
        objects = []
        paginator = self.s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=subdir, PaginationConfig={'PageSize': page_size}):
            objects.extend(obj["Key"] for obj in page.get("Contents", []))
        return objects


    def check_file_exists(self, file_name, subdir):
        """Check whether file exists in subfolder"""
        file_name_full = f'{subdir}/{file_name}'
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=file_name_full)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False # File does not exist
            raise # Raise other errors

    
    def delete_file(self, file_name, subdir):
        if self.check_file_exists(file_name, subdir):
            file_name_full = f"{subdir}/{file_name}"
            self.s3.delete_object(Bucket=self.bucket_name, Key=file_name_full)
