from PIL import Image
from io import BytesIO
import pytest
from src.utils.storage import Storage


def test_Storage_init():
    with pytest.raises(TypeError, match="Can't instantiate abstract class Storage*"):
        Storage()


@pytest.mark.parametrize("create_file", [True, False])
def test_file_exists_handler(create_file, temp_storage):
    storage = temp_storage
    subdir = 'texts'

    file_name = 'test.txt'
    storage.delete_file(file_name, subdir)
    if create_file:
        # Create init file in the path
        text_init = 'Initial content'
        storage.save_file(text_init, file_name, subdir)

    # Check all scenarios
    if create_file and storage.strategy == 'raise':
        with pytest.raises(FileExistsError, match=f'File "{file_name}" already exists*'):
            storage._file_exists_handler(file_name, 'texts')
    elif create_file and storage.strategy not in ('skip', 'rewrite', 'raise'):
        with pytest.raises(ValueError, match='"strategy" should be one*'):
            storage._file_exists_handler(file_name, 'texts')
    elif create_file and storage.strategy == 'skip' and create_file:
        assert not storage._file_exists_handler(file_name, 'texts')
    elif create_file and storage.strategy == 'rewrite' or not create_file:
        assert storage._file_exists_handler(file_name, 'texts')


@pytest.mark.parametrize("subdir,create_file", [
    ('texts', False),
    ('texts', True),
    ('text_dir', True),
])
def test_save_and_read_text(subdir, create_file, temp_storage):
    storage = temp_storage

    file_name = 'test.txt'
    storage.delete_file(file_name, subdir)
    if create_file:
        # Create init file in the path
        text_init = 'Initial content'
        storage.save_file(text_init, file_name, subdir)
    
    # Create new file in memory
    text = 'Hello, World!'

    if create_file and storage.strategy not in ('skip', 'rewrite', 'raise'):
        with pytest.raises(ValueError, match=f'"strategy" should be one of the*'):
            storage.save_file(text, file_name, subdir)
    elif create_file and storage.strategy == 'raise':
        with pytest.raises(FileExistsError, match=f'File "{file_name}" already exists*'):
            storage.save_file(text, file_name, subdir)
    else:
        # Create new file save and read it with tested function
        storage.save_file(text, file_name, subdir)
        text_read = storage.read_file(file_name, subdir)

        if not create_file or storage.strategy == 'rewrite':
            assert text_read == text
        else:
            assert text_read == text_init


@pytest.mark.parametrize("subdir,create_file", [
    ('images', False),
    ('images', True),
    ('images_dir', True),
])
def test_save_and_read_image(subdir, create_file, temp_storage):
    storage = temp_storage

    file_name = 'test.png'
    storage.delete_file(file_name, subdir)
    if create_file:
        # Create init file in the path
        img_init = Image.new(mode='RGB', size=(100, 100), color='green')
        storage.save_file(img_init, file_name, subdir)
    
    # Create new file in memory
    img = Image.new(mode='RGB', size=(10, 50), color='red')

    if create_file and storage.strategy not in ('skip', 'rewrite', 'raise'):
        with pytest.raises(ValueError, match=f'"strategy" should be one of the*'):
            storage.save_file(img, file_name, subdir)
    elif create_file and storage.strategy == 'raise':
        with pytest.raises(FileExistsError, match=f'File "{file_name}" already exists*'):
            storage.save_file(img, file_name, subdir)
    else:
        # Create new file save and read it with tested function
        storage.save_file(img, file_name, subdir)
        img_read = storage.read_file(file_name, subdir, file_type="image")
        
        # Save all images to BytesIO
        buf_img_init, buf_img, buf_img_read = BytesIO(), BytesIO(), BytesIO()
        if create_file:
            img_init.save(buf_img_init, format='PNG')
        img.save(buf_img, format='PNG')
        img_read.save(buf_img_read, format='PNG')

        if not create_file or storage.strategy == 'rewrite':
            assert buf_img_read.getvalue() == buf_img.getvalue()
        else:
            assert buf_img_read.getvalue() == buf_img_init.getvalue()


@pytest.mark.parametrize("temp_storage", [
    ("local", "rewrite"),
    ("local", "skip"),
    ("s3", "rewrite"),
    ("s3", "skip"),
], indirect=True)
def test_read_all_and_delete(temp_storage):
    storage = temp_storage
    subdir = 'text_subdir'

    num_files = 10
    for i in range(num_files):
        content = f'test_{i}'
        file_name = f'{content}.txt'
        storage.save_file(content, file_name, subdir)

    files = storage.read_all(subdir)
    assert isinstance(files, list)
    assert len(files) == num_files
    for file in files:
        assert file.split('_')[0] == 'test'
        storage.delete_file(file, subdir)
    
    files_empty = storage.read_all(subdir)
    assert not files_empty
