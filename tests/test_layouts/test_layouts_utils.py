import pytest

from src.layouts.layouts_utils import HTMLProcessor
from src.layouts.config import BACKGROUND_IMAGES, COLORS, FONTS


def test_HTMLProcessor_call_without_params(html_processor_config_without_params):
    """Test HTMLProcessor.__call__ with all awailable methods with no params"""
    config = html_processor_config_without_params
    processor = HTMLProcessor(config=config)

    params = processor({})

    assert isinstance(params, dict)
    assert params


def test_HTMLProcessor_call_with_params(html_processor_config_with_params):
    """Test HTMLProcessor.__call__ with all awailable methods with specified params"""
    config = html_processor_config_with_params
    processor = HTMLProcessor(config=config)

    params = processor({})

    assert isinstance(params, dict)
    assert params


@pytest.mark.parametrize("bg_images,proba", [
    (BACKGROUND_IMAGES, 1),
    ('bg_images', 1),
    (1, 1),
    (1, 0),
])
def test_get_bg_image(bg_images, proba):
    processor = HTMLProcessor(config=None)

    params = {}
    if not isinstance(bg_images, (str, list)) and proba:
        with pytest.raises(TypeError, match='bg_images should be*'):
            processor.get_bg_image(params, bg_images, proba)
    else:
        params = processor.get_bg_image(params, bg_images, proba)
        assert len(params) == 1
        assert 'bg_image' in params


@pytest.mark.parametrize("colors", [COLORS, ['red', 'green', 'blue']])
def test_get_colors(colors):
    processor = HTMLProcessor(config=None)

    params = {}
    params = processor.get_colors(params, colors)

    assert len(params) == 2
    assert params['bg_color'] != params['text_color']


@pytest.mark.parametrize("font_size_range,fonts", [((10, 50), FONTS)])
def test_get_font(font_size_range, fonts):
    processor = HTMLProcessor(config=None)

    params = {}
    params = processor.get_font(params, font_size_range, fonts)

    assert len(params) == 2
    assert 'font' in params
    assert 'font_size' in params


@pytest.mark.parametrize("top_range,left_range", [((10, 50), (10, 50))])
def test_get_text_position(top_range, left_range):
    processor = HTMLProcessor(config=None)

    params = {}
    params = processor.get_text_position(params, top_range, left_range)

    assert len(params) == 2
    assert 'top' in params
    assert 'left' in params


@pytest.mark.parametrize("colors,proba,highlight_padding_range,highlight_rounding_range", [
    (COLORS, 1, (1, 30), (1, 30)),
    (COLORS, 0, (1, 30), (1, 30)),
])
def test_get_highlight_params(colors, proba, highlight_padding_range, highlight_rounding_range):
    processor = HTMLProcessor(config=None)

    params = {}
    params = processor.get_colors(params, colors)
    params = processor.get_highlight_params(
        params,
        colors,
        proba,
        highlight_padding_range,
        highlight_rounding_range,
    )

    assert len(params) == 6
    assert bool(params['text_highlight_color']) == bool(proba)
    assert bool(params['highlight_padding_height']) == bool(proba)
    assert bool(params['highlight_padding_width']) == bool(proba)
    assert bool(params['highlight_rounding']) == bool(proba)
    if proba:
        assert params['bg_color'] != params['text_color'] != params['text_highlight_color']
