import copy
import os
from abc import ABC, abstractmethod
from string import Template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from math import ceil
from multiprocessing import Process

from src.utils.storage import LocalStorage, S3Storage


def generate_ui_script(images_path, boxes_path, texts_path):
    """Copy ui_template.py replacing placeholders with real paths"""

    # Define replacement values
    replacements = {
        "texts_path_placeholder": texts_path,
        "images_path_placeholder": images_path,
        "boxes_path_placeholder": boxes_path,
    }

    # Read the template script
    with open(os.path.join('src', 'utils', 'ui', 'ui_template.py'), 'r') as f:
        template_content = f.read()

    # Create Template object
    template = Template(template_content)

    # Substitute placeholders with values
    script = template.substitute(replacements)
    return script


class DataCreator(ABC):

    def __init__(self, storage_type, storage_params, subdir):
        self.storage_type = storage_type
        self.storage_params = storage_params
        self.subdir = subdir


    @abstractmethod
    def process(self):
        pass
        
    
    def __call__(self, process_params, input_data_subdir=None, dataset_size=None, start_index=0, num_processes=5):

        storage_cls = DatasetFactory.get_storage(self.storage_type)
        storage_params_copy = copy.deepcopy(self.storage_params)
        storage = storage_cls(**storage_params_copy)

        if input_data_subdir and not dataset_size:
            file_names = storage.read_all(input_data_subdir)[start_index:]
        elif dataset_size and not input_data_subdir:
            file_names = range(dataset_size)[start_index:]
        else:
            raise ValueError('One should provide either "input_data_subdir" or "dataset_size"')
        
        chunk_size = ceil(len(file_names) / num_processes)
        processes = []
        process_params.update({
            'subdir': self.subdir,
            'input_data_subdir': input_data_subdir,
            'dataset_size': dataset_size,
            'storage_type': self.storage_type,
            'storage_params': self.storage_params,
        })

        for chunk_num in range(num_processes):
            chunk = file_names[chunk_num * chunk_size:(chunk_num + 1) * chunk_size]
            process_params['file_names'] = chunk
            process_params['chunk_num'] = chunk_num
            pr = Process(
                target=self.process,
                kwargs=process_params,
            )
            processes.append(pr)
            pr.start()

        for pr in processes:
            pr.join()
        

class BaseProcessor:

    def __init__(self, config):
        self.config = config
        self.methods = {}
        self.necessary_methods = []
        
        
    def __call__(self, obj=None):
        for method_name, method in self.methods.items():
            if method_name in self.config or method_name in self.necessary_methods:
                params = self.config.get(method_name) or {}
                if object is not None:
                    obj = method(obj, **params)
                else:
                    method(**params)
        return obj
    

class DatasetFactory:

    @classmethod
    def get_storage(self, storage_type='local'):
        classes = {'local': LocalStorage, 'S3': S3Storage}
        return classes[storage_type]


def set_driver(driver_path, download_dir=None):
    
    options = Options()
    if download_dir:
        options = webdriver.ChromeOptions()
        prefs = {
            "profile.default_content_settings.popups": 0,
            "download.default_directory": os.path.abspath(download_dir),
            "directory_upgrade": True,
        }
        options.add_experimental_option("prefs", prefs)
    options.add_argument("--headless") # Run in headless mode
    service = Service(driver_path)
    driver = webdriver.Chrome(options=options, service=service)
    return driver
