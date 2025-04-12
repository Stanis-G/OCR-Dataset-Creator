import os
import tempfile
from PIL import Image
from io import BytesIO
import pytest
from utils.storage import Storage, LocalStorage, S3Storage


def test_Storage_init():
    with pytest.raises(TypeError, match="Can't instantiate abstract class Storage*"):
        Storage()


@pytest.mark.parametrize("strategy,create_file", [
    ('skip', True),
    ('rewrite', True),
    ('raise', True),
    ('nonvalid', True),
    (5, True),
    ('skip', False),
])
def test_file_exists_handler(strategy, create_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(tmpdir, file_exists_strategy=strategy)

        # Create file in the path
        file_name = 'test.txt'
        file_dir = os.path.join(tmpdir, 'texts')
        os.makedirs(file_dir, exist_ok=True)
        if create_file:
            text_init = 'Initial content'
            with open(os.path.join(file_dir, file_name), 'w') as f:
                f.write(text_init)
        else:
            assert storage._file_exists_handler(file_name, 'texts')

        # Check all scenarios
        if strategy == 'raise':
            with pytest.raises(FileExistsError, match=f'File "{file_name}" already exists*'):
                storage._file_exists_handler(file_name, 'texts')
        elif strategy not in ('skip', 'rewrite', 'raise'):
            with pytest.raises(ValueError, match='"strategy" should be one*'):
                storage._file_exists_handler(file_name, 'texts')
        elif strategy == 'skip' and create_file:
            assert not storage._file_exists_handler(file_name, 'texts')
        elif strategy == 'rewrite':
            assert storage._file_exists_handler(file_name, 'texts')


@pytest.mark.parametrize("subdir,strategy,create_file", [
    ('texts', 'skip', False),
    ('texts', 'skip', True),
    ('texts', 'rewrite', False),
    ('texts', 'rewrite', True),
    ('text_dir', 'rewrite', True),
])
def test_local_save_and_read_text(subdir, strategy, create_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(tmpdir, file_exists_strategy=strategy)

        file_name = 'test.txt'
        if create_file:
            # Create file in the path
            text_init = 'Initial content'
            storage.save_file(text_init, file_name, subdir)
        else:
            assert storage._file_exists_handler(file_name, subdir)

        # Create new file save and read it with tested function
        text = 'Hello, World!'
        file_name = 'test.txt'
        storage.save_file(text, file_name, subdir)
        text_read = storage.read_file(file_name, subdir)

        if not create_file or strategy == 'rewrite':
            assert text_read == text
        else:
            assert text_read == text_init


@pytest.mark.parametrize("subdir,strategy,create_file", [
    ('images', 'skip', False),
    ('images', 'skip', True),
    ('images', 'rewrite', False),
    ('images', 'rewrite', True),
    ('images_dir', 'rewrite', True),
])
def test_local_save_and_read_image(subdir, strategy, create_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(tmpdir, file_exists_strategy=strategy)

        file_name = 'test.png'
        if create_file:
            # Create init file in the path
            img_init = Image.new(mode='RGB', size=(100, 100), color='green')
            storage.save_file(img_init, file_name, subdir)
        else:
            assert storage._file_exists_handler(file_name, subdir)

        # Create new file save and read it with tested function
        img = Image.new(mode='RGB', size=(10, 50), color='red')
        storage.save_file(img, file_name, subdir)
        img_read = storage.read_file(file_name, subdir, file_type="image")
        
        # Save all images to BytesIO
        buf_img_init, buf_img, buf_img_read = BytesIO(), BytesIO(), BytesIO()
        if create_file:
            img_init.save(buf_img_init, format='PNG')
        img.save(buf_img, format='PNG')
        img_read.save(buf_img_read, format='PNG')

        if not create_file or strategy == 'rewrite':
            assert buf_img_read.getvalue() == buf_img.getvalue()
        else:
            assert buf_img_read.getvalue() == buf_img_init.getvalue()
