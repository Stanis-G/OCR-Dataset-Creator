import io
import numpy as np
import pytest

from images.image_utils import ImageProcessor


def test_ImageProcessor_call_without_params(get_image, image_processor_config_without_params):
    """Test HTMLProcessor.__call__ with all awailable methods with no params"""
    config = image_processor_config_without_params
    processor = ImageProcessor(config=config)

    img = get_image
    img_out = processor(img)

    buf, buf_out = io.BytesIO(), io.BytesIO()
    img.save(buf, format='PNG')
    img_out.save(buf_out, format='PNG')

    assert buf.getvalue() != buf_out.getvalue()


def test_ImageProcessor_call_with_params(get_image, image_processor_config_with_params):
    """Test HTMLProcessor.__call__ with all awailable methods with specified params"""
    config = image_processor_config_with_params
    processor = ImageProcessor(config=config)

    img = get_image
    img_out = processor(img)

    buf, buf_out = io.BytesIO(), io.BytesIO()
    img.save(buf, format='PNG')
    img_out.save(buf_out, format='PNG')

    assert buf.getvalue() != buf_out.getvalue()


@pytest.mark.parametrize("center,glare_relative_radius,glare_intensity,blur_strength", [
    ((0.5, 0.5), 0.3, 0.5, 100),
    ((-0.5, 0.5), 2, 0.5, 101),
    ((0.5, -0.5), 0.3, 1.5, 100),
    ((0.5, 0.5), 0.3, 1.5, -100),
])
def test_add_glare(get_image_as_array, center, glare_relative_radius, glare_intensity, blur_strength):
    processor = ImageProcessor(config=None)

    img = get_image_as_array
    img_out = processor.add_glare(img, center, glare_relative_radius, glare_intensity, blur_strength)

    assert not np.array_equal(img, img_out)


@pytest.mark.parametrize("center_range,glare_relative_radius_range,glare_intensity_range,blur_strength_range", [
    ((0.2, 0.6), (-0.1, 0.5), (0.1, 0.6), (50, -60)),
    ((-0.2, 0.6), (0.1, -0.5), (0.1, 0.6), (-50, 60)),
    ((0.2, -0.6), (0.1, 0.5), (-0.1, 0.6), (50, 60)),
    ((0.2, 0.6), (0.1, 0.5), (0.1, -0.6), (50, -60)),
])
def test_add_random_glare(
    get_image_as_array,
    center_range,
    glare_relative_radius_range,
    glare_intensity_range,
    blur_strength_range,
):
    processor = ImageProcessor(config=None)

    img = get_image_as_array
    img_out = processor.add_random_glare(
        img,
        center_range,
        glare_relative_radius_range,
        glare_intensity_range,
        blur_strength_range,
    )

    assert isinstance(img_out, np.ndarray)


@pytest.mark.parametrize("blur_type,ksize", [
    ('gaussian', 3),
    ('gaussian', 4),
    ('median', 3),
    ('median', 4),
    ('avg', 3),
    ('avg', 4),
    ('gaussian', 0),
    ('avg', 1),
    ('invalid', 5),
])
def test_blur(get_image_as_array, blur_type, ksize):
    processor = ImageProcessor(config=None)

    img = get_image_as_array
    if blur_type not in ('gaussian', 'median', 'avg'):
        with pytest.raises(ValueError, match=".*'blur_type' is not valid"):
            processor.blur(img, blur_type, ksize)
    else:
        img_out = processor.blur(img, blur_type, ksize)
        assert isinstance(img_out, np.ndarray)


@pytest.mark.parametrize("width_range,height_range", [
    ((500, 1500), (500, 1500)),
    ((0, 1500), (500, 400)),
])
def test_random_resize(get_image_as_array, width_range, height_range):
    processor = ImageProcessor(config=None)

    img = get_image_as_array
    img_out = processor.random_resize(img, width_range, height_range)
    
    assert img_out.shape != img.shape


@pytest.mark.parametrize("mean,std", [(0, 0.1), (5, 10)])
def test_add_gaussian_noise(get_image_as_array, mean, std):
    processor = ImageProcessor(config=None)

    img = get_image_as_array
    img_out = processor.add_gaussian_noise(img, mean, std)
    
    assert isinstance(img_out, np.ndarray)


@pytest.mark.parametrize("proba", [0.3, 1.2])
def test_add_impulse_noise(get_image_as_array, proba):
    processor = ImageProcessor(config=None)

    img = get_image_as_array
    img_out = processor.add_impulse_noise(img, proba)
    
    assert isinstance(img_out, np.ndarray)
