import asyncio
from io import BytesIO
import sys
import shutil
from pathlib import Path
from PIL import Image

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import os
from urllib.request import pathname2url
import numpy as np
from utils.utils import set_driver, save_fileobj_to_s3, list_objects_in_bucket, read_file_from_s3
from images.image_utils import ImageProcessor


class ImageCreator:
    """Add visual effects to image to enable OCR model recognize text in complex conditions"""
    
    def __init__(self, bucket_name, driver_path):
        self.bucket_name = bucket_name
        self.driver_path = driver_path


    def __call__(self, processor_config, status_every=1000):

        self.processor = ImageProcessor(processor_config)

        driver = set_driver(self.driver_path)

        os.makedirs('tmp/pages')
        for i, file_name in enumerate(list_objects_in_bucket(self.bucket_name, prefix='pages', page_size=1000)):

            # Get html page from S3 by URL
            num = int(file_name.split('_')[1].split('.')[0])
            page = read_file_from_s3(file_name, self.bucket_name)

            # Temporary save file and read it using driver
            rel_path = f'tmp/{file_name}'
            with open(rel_path, 'w') as f:
                f.write(page)
            file_path = os.path.abspath(rel_path)
            url = f"file://{file_path}" 
            driver.get(url)

            # Hide scrollbar with JavaScript
            driver.execute_script("document.body.style.overflow = 'hidden';")

            # Take and preprocess a screenshot
            img = driver.get_screenshot_as_png()
            img = self.processor(img)

            # Save image to S3
            img_name = f'image_{num}.png'
            save_fileobj_to_s3(img, img_name, self.bucket_name, prefix='images')

            if status_every and i % status_every == 0:
                print(i)

        shutil.rmtree('tmp')


class AsyncImageIterator:

    def __init__(self, input_path, driver):
        self.input_path = input_path
        self.driver = driver
        self.files = os.listdir(self.input_path)
        self.ind = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.ind < len(self.files):
            cur_ind = self.ind
            input_filepath = os.path.join(os.getcwd(), self.input_path, f'page_{cur_ind}.html')
            input_filepath = os.path.normpath(input_filepath)
            url = 'file:' + pathname2url(input_filepath)
            await asyncio.to_thread(self.driver.get, url)
            self.ind += 1
        else:
            raise StopAsyncIteration
        return self.ind, input_filepath
    

class AsyncImageProcessor:
    """Add visual effects to image to enable OCR model recognize text in complex conditions"""
    
    def __init__(self, input_path, output_path, driver_path):
        self.input_path = input_path
        self.output_path = output_path
        self.driver_path = driver_path
        self.lock = asyncio.Lock()

    def process_image(self, img):
        img = Image.open(BytesIO(img))
        img = np.array(img)
        if self.process_funcs:
            for func, kwargs in self.process_funcs.items():
                img = func(img, **kwargs)
        img = Image.fromarray(img)
        return img
        
    async def save_screenshot(self, input_filepath, output_path, image_ind, driver, semaphore):
        screenshot_path = os.path.join(output_path, f'image_{image_ind}.png')
        async with self.lock:
            if os.path.exists(input_filepath) and not os.path.exists(screenshot_path):
                img = driver.get_screenshot_as_png()
                img = self.process_image(img)
                async with semaphore:
                    await asyncio.to_thread(img.save, screenshot_path)

    async def __call__(self, process_funcs={}, num_concurrent=10, num_loaded_tasks=1000):

        self.process_funcs = process_funcs
        os.makedirs(self.output_path, exist_ok=True)
        driver = set_driver(self.driver_path)

        tasks = []
        semaphore = asyncio.Semaphore(num_concurrent)
        try:
            async for image_ind, input_filepath in AsyncImageIterator(self.input_path, driver):
                task = asyncio.create_task(self.save_screenshot(input_filepath, self.output_path, image_ind, driver, semaphore))
                tasks.append(task)
                if len(tasks) > num_loaded_tasks:
                    await asyncio.gather(*tasks)
                    tasks.clear()     
            await asyncio.gather(*tasks)
        finally:
            driver.quit()
