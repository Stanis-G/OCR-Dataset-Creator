import argparse
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from src.dataset.dataset import OCRDataset
from src.htmls.htmls import HTMLCreator
from src.parsers.parsers import WikiParser
from src.processors.processors import ImageProcessor
from src.utils.config import FONTS, COLORS, BACKGROUND_IMAGES


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-o', '--output_folder', nargs=1, default='ocr_dataset', type=str)
output_folder = arg_parser.parse_args().output_folder[0]
driver_path = 'chromedriver-win64/chromedriver.exe'

parser = WikiParser()
html_creator = HTMLCreator(
        fonts=FONTS,
        text_colors=COLORS,
        background_images=BACKGROUND_IMAGES,
        background_colors=COLORS,
        font_size=(5, 45),
        top=(5, 75),
        left=(5, 75),
    )
processor = ImageProcessor(driver_path=driver_path)
dataset = OCRDataset(parser=parser, html_creator=html_creator, image_processor=processor)

parser_args = dict(dataset_size=100000, status_every=1000)
data = dataset(output_folder=output_folder, data_exists_handler='complete', parser_args=parser_args)
