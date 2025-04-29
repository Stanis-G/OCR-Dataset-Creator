import argparse
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from src.dataset.dataset import OCRDataset
from src.layouts.layouts import HTMLCreator
from src.parsers.parsers import WikiParser
from src.images.images import ImageCreator
from src.layouts.config import FONTS, COLORS
from src.utils.storage import LocalStorage


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-n', '--name', nargs='?', default='ocr-dataset', type=str)
arg_parser.add_argument('-s', '--size', nargs='?', default=1000, type=int)

dataset_name = arg_parser.parse_args().name
dataset_size = arg_parser.parse_args().size
driver_path = 'chromedriver-win64/chromedriver.exe'

text_processor_config = {
    'remove_section_headers': {},
    'remove_non_ascii_symbols': {},
    'remove_references': {},
    'remove_latex': {},
    'strip_sentences': {},
    'remove_short_sentences': {'min_len': 3},
    'update_token_counts': {},
}
html_processor_config = {
    'get_bg_image': dict(
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
image_processor_config = {
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
        mean_range=(0, 5),
        std_range=(0, 5),
    ),
    'add_random_impulse_noise': dict(
        proba_range=(0, 0.03),
    ),
}

dataset = OCRDataset(
    driver_path=driver_path,
    parser=WikiParser,
    html_creator=HTMLCreator,
    image_creator=ImageCreator,
    storage=LocalStorage(dataset_name=dataset_name)
)
dataset(
    text_processor_config=text_processor_config,
    html_processor_config=html_processor_config,
    image_processor_config=image_processor_config,
    dataset_size=dataset_size,
)
