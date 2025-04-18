import numpy as np
from PIL import Image
import pytest


@pytest.fixture
def get_image():
    img = Image.new('RGB', (100, 100), color='red')
    return img


@pytest.fixture
def get_image_as_array():
    img = Image.new('RGB', (100, 100), color='red')
    return np.array(img)
    

@pytest.fixture
def image_processor_config_without_params():
    config = {
        'add_random_glare': {},
        'random_blur': {},
        'radnom_resize': {},
        'add_random_gaussian_noise': {},
        'add_random_impulse_noise': {},
    }
    return config


@pytest.fixture
def image_processor_config_with_params():
    config = {
        'add_random_glare': dict(
            center_range=(0, 1),
            glare_relative_radius_range=(0.1, 0.5),
            glare_intensity_range=(0.1, 0.5),
            blur_strength_range=(121, 251),
        ),
        'random_blur': dict(
            blur_type_values=('avg', 'median', 'gaussian'),
            ksize_range=(3, 8),
        ),
        'radnom_resize': dict(
            width_range=(500, 1500),
            height_range=(500, 1500),
        ),
        'add_random_gaussian_noise': dict(
            mean_range=(0, 10),
            std_range=(0, 10),
        ),
        'add_random_impulse_noise': dict(
            proba_range=(0, 0.05),
        ),
    }
    return config
