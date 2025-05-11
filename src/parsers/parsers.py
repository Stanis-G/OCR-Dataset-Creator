from bs4 import BeautifulSoup
import copy
import sys
import requests
from requests.exceptions import ReadTimeout
from tqdm import tqdm
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import os
from parsers.parser_utils import TextProcessor
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from utils.utils import DataCreator, DatasetFactory, set_driver


class WikiParser(DataCreator):

    def __init__(self, storage_type, storage_params, subdir='texts'):
        super().__init__(storage_type, storage_params, subdir)
        self.WIKI_API_URL = "https://en.wikipedia.org/w/api.php"


    def get_random_wikipedia_title(self):
        """Fetches a random Wikipedia page title."""
        params = {
            "action": "query",
            "list": "random",
            "rnnamespace": 0, # Only main articles (not Talk, User, etc.)
            "format": "json"
        }
        response = requests.get(self.WIKI_API_URL, params=params).json()
        return response["query"]["random"][0]["title"]


    def get_soup(self, page_title, timeout=10):
        """Fetches section titles from a given Wikipedia page."""
        params = {
            "action": "parse",
            "page": page_title,
            "format": "json",
            "prop": "text"
        }
        try:
            response = requests.get(self.WIKI_API_URL, params=params, timeout=timeout).json()
        except ReadTimeout:
            return None
        if "error" in response:
            return [] # Skip pages with issues
        html_content = response.get("parse", {}).get("text", {}).get("*", "")

        soup = BeautifulSoup(html_content, "html.parser")
        return soup


    def process(self, file_names, subdir, processor_config, storage_type, storage_params, chunk_num, delay=0.05, **kwargs):
        """Collects Wikipedia section titles until reaching the target count."""
        storage_cls = DatasetFactory.get_storage(storage_type)
        storage_params_copy = copy.deepcopy(storage_params)
        storage = storage_cls(**storage_params_copy)
        processor = TextProcessor(processor_config)

        for num in tqdm(file_names, position=chunk_num, desc=f'Process {chunk_num}'):

            # Parse and process data
            page_title = self.get_random_wikipedia_title()
            soup = self.get_soup(page_title)
            if not soup:
                continue
            sentences = processor(soup)

            for text in sentences:

                file_name = f'title_{num}.txt'
                storage.save_file(text, file_name, subdir)
            time.sleep(delay) # Avoid hitting API rate limits
        
        # # Postprocessing
        # if 'update_token_counts' in processor_config and start_index < dataset_size:
        #     processor.save_state('token_counts.json')
        #     processor.calc_probas()
        #     # Read every saved file, postprocess and rewrite it
        #     for file_name in tqdm(storage.read_all(subdir)):
        #         text = storage.read_file(file_name, subdir, file_type='text')
        #         text = processor.remove_frequent_tokens(text)
        #         storage.save_file(text, file_name, subdir)


class YouTubeParser:

    def __init__(self, driver_path, output_path):
        self.output_path = output_path
        self.driver_path = driver_path


    def __call__(self, search_query, delay=0.05):

        os.makedirs(self.output_path, exist_ok=True)
        driver = set_driver(self.driver_path)

        try:
            # Build the YouTube search URL
            url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"

            # Navigate to the page
            driver.get(url)

            # Allow some time for the page to load
            time.sleep(delay)

            # Extract video titles
            video_titles = []
            videos = driver.find_elements(By.CSS_SELECTOR, "h3 a#video-title")
            for video in videos:
                video_titles.append(video.text)

            # Write titles as txt files
            for num, title in enumerate(video_titles):
                with open(os.path.join(self.output_path, f'title_{num}.txt'), 'w', encoding='utf-8') as f:
                    f.write(title)

        finally:
            # Close the browser
            driver.quit()


class PowerPointTemplateParser:

    def __init__(self, output_path, driver_path):
        self.driver_path = driver_path
        self.output_path = output_path

    def __call__(self):
        os.makedirs(self.output_path, exist_ok=True)
        main_page_url = "https://create.microsoft.com/ru-ru/search?filters=presentations"

        try:
            # Open the main page with all presentations
            driver = set_driver(self.driver_path, download_dir=self.output_path)
            driver.get(main_page_url)
            time.sleep(3)  # Allow time for the page to load

            # Find all presentation links
            presentation_blocks = driver.find_elements(By.CSS_SELECTOR, "div.MasonryGrid_itemWrapper__FxODS a")

            # Add URLs to list
            urls = []
            for block in presentation_blocks:
                href = block.get_attribute("href")
                if href:
                    urls.append(href)

            # Push Download button
            for url in urls:
                driver.get(url)
                time.sleep(5) # Wait for the page to load

                try:
                    # Locate and click the button by its text
                    button = driver.find_element(By.XPATH, "//span[contains(text(), 'Скачать')]")
                    ActionChains(driver).move_to_element(button).click().perform()
                    print(f"Downloaded: {url}")
                
                except Exception as e:
                    print(f"Failed on {url}: {e}")

                # Wait before moving to the next page
                time.sleep(3)
        finally:
            driver.quit()
