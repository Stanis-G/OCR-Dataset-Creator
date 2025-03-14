import argparse
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from src.dataset.dataset import OCRDataset
from layouts.layouts import HTMLCreator
from src.parsers.parsers import WikiParser
from src.images.images import ImageCreator
from src.layouts.config import FONTS, COLORS, BACKGROUND_IMAGES


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-o', '--bucket_name', nargs='?', default='ocr-dataset', type=str)
arg_parser.add_argument('-d', '--dataset_size', nargs='?', default=1000, type=int)
arg_parser.add_argument('-s', '--status_every', nargs='?', default=1000, type=int)

bucket_name = arg_parser.parse_args().bucket_name
dataset_size = arg_parser.parse_args().dataset_size
status_every = arg_parser.parse_args().status_every
driver_path = 'chromedriver-win64/chromedriver.exe'

text_processor_config = [
    'remove_section_headers',
    'remove_non_ascii_symbols',
    'remove_references',
    'remove_latex',
    'strip_sentences',
    'remove_frequent_tokens',
]
html_processor_config = {
    'bg_images': BACKGROUND_IMAGES,
    'bg_colors': COLORS,
    'text_colors': COLORS,
    'fonts': FONTS,
    'font_size': (20, 45),
    'top': (5, 75),
    'left': (5, 75),
}
image_processor_config = {
    'methods': ['add_random_glare', 'random_blur'],
    'params': [
        dict(
            center_range=(0, 1),
            glare_relative_radius_range=(0.1, 0.5),
            glare_intensity_range=(0.1, 0.5),
            blur_strength_range=(121, 251),
        ),
        dict(
            blur_type_values=('avg', 'median', 'gaussian'),
            ksize_range=(3, 8),
        )
    ],
}

dataset = OCRDataset(
    driver_path=driver_path,
    parser=WikiParser,
    html_creator=HTMLCreator,
    image_creator=ImageCreator,
    bucket_name=bucket_name,
)
dataset(
    text_processor_config=text_processor_config,
    html_processor_config=html_processor_config,
    image_processor_config=image_processor_config,
    dataset_size=dataset_size,
    status_every=status_every,
)
