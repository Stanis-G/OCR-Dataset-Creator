import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

load_dotenv()
MINIO_URL = os.getenv("MINIO_URL")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")


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
