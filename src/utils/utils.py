import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from src.utils.storage import Storage


class DataCreator:

    def __init__(self, storage, subdir):
        self.storage = storage
        self.subdir = subdir
        if not isinstance(self.storage, Storage):
            raise TypeError('"storage" should be a subclass of "Storage"')
        if not isinstance(self.subdir, str):
            raise TypeError('"subdir" should be str')
        

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
