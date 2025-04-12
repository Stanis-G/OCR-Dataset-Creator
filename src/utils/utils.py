import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from .storage import Storage


class DataCreator:

    def __init__(self, storage, subdir):
        self.storage = storage
        self.subdir = subdir
        if not isinstance(self.storage, Storage):
            raise TypeError('"storage" should be a subclass of "Storage"')
        if not isinstance(self.subdir, str):
            raise TypeError('"subdir" should be str')


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
