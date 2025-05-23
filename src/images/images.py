import copy
import sys
from tqdm import tqdm
from pathlib import Path
import urllib

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import os
from utils.utils import DataCreator, DatasetFactory, set_driver
from images.image_utils import ImageProcessor, get_yolo_bounding_box


class ImageCreator(DataCreator):
    """Add visual effects to image to enable OCR model recognize text in complex conditions"""
    
    def __init__(self, storage_type, storage_params, driver_path, subdir='images', bbox_subdir=None):
        super().__init__(storage_type, storage_params, subdir)
        self.driver_path = driver_path
        self.bbox_subdir = bbox_subdir


    def process(self, file_names, subdir, input_data_subdir, bbox_subdir, processor_config, storage_type, storage_params, chunk_num, **kwargs):
        storage_cls = DatasetFactory.get_storage(storage_type)
        storage_params_copy = copy.deepcopy(storage_params)
        storage = storage_cls(**storage_params_copy)
        processor = ImageProcessor(processor_config)
        driver = set_driver(self.driver_path)
        for file_name in tqdm(file_names, position=chunk_num, desc=f'Process {chunk_num}'):
            
            # Get html page, inject into browser and get its url
            page = storage.read_file(file_name, input_data_subdir, file_type='text')
            url = "data:text/html;charset=utf-8," + urllib.parse.quote(page)
            driver.get(url)

            # Hide scrollbar with JavaScript
            driver.execute_script("document.body.style.overflow = 'hidden';")

            # Take and preprocess a screenshot
            img = driver.get_screenshot_as_png()
            img = processor(img, bytes_like=True)

            # Save image
            num = int(file_name.split('_')[1].split('.')[0])
            img_name = f'image_{num}'
            storage.save_file(img, f'{img_name}.png', subdir)

            if bbox_subdir:
                # Get bounding box coordinates and canvas sizes
                js_script_path = os.path.join('src', 'images', 'js', 'get_bbox_coords.js')
                with open(js_script_path, 'r') as f:
                    js_script = f.read()
                coords = driver.execute_script(js_script)
                width = driver.execute_script("return document.documentElement.scrollWidth")
                height = driver.execute_script("return document.documentElement.scrollHeight")

                # Calculate bounding box in YOLO format and
                # save under the image name for ultralytics dataset consistency
                coords_yolo = get_yolo_bounding_box(coords, width, height)
                storage.save_file(coords_yolo, f'{img_name}.txt', bbox_subdir)
