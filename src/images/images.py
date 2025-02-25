import asyncio
from io import BytesIO
import sys
from pathlib import Path
from PIL import Image

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import os
from urllib.request import pathname2url
import numpy as np
import cv2
from utils.utils import set_driver


class ImageCreator:
    """Add visual effects to image to enable OCR model recognize text in complex conditions"""
    
    def __init__(self, input_path, output_path, driver_path):
        self.input_path = input_path
        self.output_path = output_path
        self.driver_path = driver_path

    def process_image(self, img, process_funcs={}):
        img = Image.open(BytesIO(img))
        img = np.array(img)
        if process_funcs:
            for func, kwargs in process_funcs.items():
                img = func(img, **kwargs)
        img = Image.fromarray(img)
        return img

    def __call__(self, process_funcs={}):

        os.makedirs(self.output_path, exist_ok=True)
        driver = set_driver(self.driver_path)

        for num in range(len(os.listdir(self.input_path))):

            input_filepath = os.path.join(os.getcwd(), self.input_path, f"page_{num}.html")
            input_filepath = os.path.normpath(input_filepath)
            url = 'file:' + pathname2url(input_filepath)
            screenshot_path = os.path.join(self.output_path, f'image_{num}.png')

            if os.path.exists(input_filepath) and not os.path.exists(screenshot_path):
                driver.get(url)

                # Hide scrollbar with JavaScript
                driver.execute_script("document.body.style.overflow = 'hidden';")

                # Take and preprocess a screenshot
                img = driver.get_screenshot_as_png()
                img = self.process_image(img, process_funcs)
                img.save(screenshot_path)


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
