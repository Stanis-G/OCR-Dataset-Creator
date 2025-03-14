import argparse
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from tqdm import tqdm

from src.dataset.dataset import OCRDataset
from src.layouts.layouts import HTMLCreator
from src.parsers.parsers import YouTubeParser
from src.images.images import ImageCreator
from src.layouts.config import FONTS, COLORS, BACKGROUND_IMAGES

from queries import QUERIES


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-o', '--output_folder', nargs=1, default='ocr_dataset', type=str)
output_folder = arg_parser.parse_args().output_folder[0]
driver_path = 'chromedriver-win64/chromedriver.exe'

parser = YouTubeParser(driver_path=driver_path)
html_creator = HTMLCreator(
        fonts=FONTS,
        text_colors=COLORS,
        background_images=BACKGROUND_IMAGES,
        background_colors=COLORS,
        font_size=(5, 45),
        top=(5, 75),
        left=(5, 75),
    )
processor = ImageCreator(driver_path=driver_path)
dataset = OCRDataset(parser=parser, html_creator=html_creator, image_processor=processor)

for search_query in tqdm(QUERIES, leave=False):
    parser_args = dict(search_query=search_query)
    data = dataset(output_folder=output_folder, data_exists_handler='complete', parser_args=parser_args)
