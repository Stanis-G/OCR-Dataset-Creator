import os
from PIL import Image
from io import BytesIO
import pytest
from utils.storage import Storage, LocalStorage, S3Storage


def test_Storage_init():
    with pytest.raises(TypeError, match="Can't instantiate abstract class Storage*"):
        Storage()


@pytest.mark.parametrize("subdir", ['texts', 'text_dir'])
def test_local_save_and_read_text(subdir, temp_local_storage):
    storage = temp_local_storage
    os.makedirs(os.path.join(storage.data_dir, subdir), exist_ok=True)
    
    text = 'Hello, World!'
    file_name = 'test_file.txt'
    storage.save_file(text, file_name, subdir)
    text_read = storage.read_file(file_name, subdir)

    assert text == text_read


@pytest.mark.parametrize("subdir", ['images', 'images_dir'])
def test_local_save_and_read_image(subdir, temp_local_storage):
    storage = temp_local_storage
    os.makedirs(os.path.join(storage.data_dir, subdir), exist_ok=True)

    img = Image.new("RGB", (10, 10), color="red")
    file_name = "image.png"
    storage.save_file(img, file_name, subdir)
    img_read = storage.read_file(file_name, subdir, file_type="image")
    
    buf_img, buf_img_read = BytesIO(), BytesIO()
    img.save(buf_img, format='PNG')
    img_read.save(buf_img_read, format='PNG')

    assert buf_img.getvalue() == buf_img_read.getvalue()
