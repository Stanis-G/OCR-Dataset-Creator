import os
from string import Template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from src.utils.storage import Storage


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
