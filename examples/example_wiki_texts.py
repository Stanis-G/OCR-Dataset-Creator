import argparse
import asyncio
import os
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from src.layouts.htmls import HTMLCreator
from src.parsers.parsers import AsyncWikiParser
from images.images import ImageCreator
from src.utils.config import FONTS, COLORS, BACKGROUND_IMAGES
from src.images.image_utils import add_random_glare, random_blur


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-o', '--output_folder', nargs='?', default='ocr_dataset', type=str)
arg_parser.add_argument('-d', '--dataset_size', nargs='?', default=1000, type=int)

output_folder = arg_parser.parse_args().output_folder
dataset_size = arg_parser.parse_args().dataset_size
driver_path = 'chromedriver-win64/chromedriver.exe'
image_process_funcs = {
    add_random_glare: dict(
        center_range=(0, 1),
        glare_relative_radius_range=(0.1, 0.5),
        glare_intensity_range=(0.1, 0.5),
        blur_strength_range=(121, 251),
    ),
    random_blur: dict(
        blur_type_values=('avg', 'median', 'gaussian'),
        ksize_range=(3, 8),
    )
}

os.makedirs(output_folder, exist_ok=True)
text_path = os.path.join(output_folder, 'texts')
html_path = os.path.join(output_folder, 'pages')
image_path = os.path.join(output_folder, 'images')

# Create objects
parser = AsyncWikiParser(
    output_path=text_path,
)
html_creator = HTMLCreator(
    input_path=text_path,
    output_path=html_path,
)
image_processor = ImageCreator(
    input_path=html_path,
    output_path=image_path,
    driver_path=driver_path,
)

# Run dataset parsing and processing
asyncio.run(parser(
    dataset_size=dataset_size,
    status_every=1000,
    delay=0.05,
    num_concurrent=15,
))
html_creator(
    fonts=FONTS,
    text_colors=COLORS,
    background_images=BACKGROUND_IMAGES,
    background_colors=COLORS,
    font_size=(20, 45),
    top=(5, 75),
    left=(5, 75),
)
image_processor(
    process_funcs=image_process_funcs,
)
