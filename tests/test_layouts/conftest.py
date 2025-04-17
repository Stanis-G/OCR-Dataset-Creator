import pytest

from layouts.config import COLORS, FONTS


@pytest.fixture
def html_processor_config_without_params():
    config = {
        'get_bg_images': {},
        'get_colors': {},
        'get_font': {},
        'get_text_position': {},
        'get_hihglight_params': {},
    }
    return config


@pytest.fixture
def html_processor_config_with_params():
    config = {
        'get_bg_images': dict(
            bg_images='bg_images',
            proba=0.5,
        ),
        'get_colors': dict(
            colors=COLORS,
        ),
        'get_font': dict(
            font_size_range=(20, 40),
            fonts=FONTS,
        ),
        'get_text_position': dict(
            top_range=(5, 75),
            left_range=(5, 75),
        ),
        'get_hihglight_params': dict(
            colors=COLORS,
            proba=0.5,
            highlight_padding_range=(1, 30),
            highlight_rounding_range=(1, 15),
        ),
    }
    return config
