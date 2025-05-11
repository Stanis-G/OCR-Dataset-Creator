import pytest
from src.utils.utils import generate_ui_script


@pytest.mark.parametrize("images_path,boxes_path,texts_path", [
    ('images', 'boxes', 'texts'),
    (10, None, [20, 30]),
])
def test_generate_ui_script(images_path, boxes_path, texts_path):

    script = generate_ui_script(images_path, boxes_path, texts_path)
    assert 'placeholder' not in script
