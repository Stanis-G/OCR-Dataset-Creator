import os
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from src.dataset.dataset import OCRDataset
from src.layouts.layouts import HTMLCreator
from src.parsers.parsers import WikiParser
from src.images.images import ImageCreator
from src.layouts.config import FONTS, COLORS
from src.utils.storage import S3Storage

load_dotenv()

client_config = dict(
    endpoint_url=os.getenv("MINIO_URL"),
    aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
    aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
)

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
    'remove_frequent_tokens': {},
}
html_processor_config = {
    'bg_images': 'bg_images',
    'bg_colors': COLORS,
    'text_colors': COLORS,
    'text_highlight_colors': COLORS,
    'highlight_padding': (1, 30),
    'highlight_rounding': (1, 15),
    'fonts': FONTS,
    'font_size': (20, 45),
    'top': (5, 75),
    'left': (5, 75),
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
        mean_range=(0, 10),
        std_range=(0, 10),
    ),
    'add_random_impulse_noise': dict(
        proba_range=(0, 0.05),
    ),
}

dataset = OCRDataset(
    driver_path=driver_path,
    parser=WikiParser,
    html_creator=HTMLCreator,
    image_creator=ImageCreator,
    storage=S3Storage(dataset_name=dataset_name, client_config=client_config),
)
dataset(
    text_processor_config=text_processor_config,
    html_processor_config=html_processor_config,
    image_processor_config=image_processor_config,
    dataset_size=dataset_size,
)
