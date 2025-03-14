import asyncio
from bs4 import BeautifulSoup
import requests
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import os
from parsers.parser_utils import TextProcessor
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from utils.utils import set_driver, save_fileobj_to_s3


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


class WikiParser:

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
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


    def get_sentences(self, page_title):
        """Fetches section titles from a given Wikipedia page."""
        params = {
            "action": "parse",
            "page": page_title,
            "format": "json",
            "prop": "text"
        }
        response = requests.get(self.WIKI_API_URL, params=params).json()
        if "error" in response:
            return [] # Skip pages with issues
        html_content = response.get("parse", {}).get("text", {}).get("*", "")

        soup = BeautifulSoup(html_content, "html.parser")
        sentences = self.processor(soup)

        return sentences


    def __call__(self, processor_config, dataset_size=10000, status_every=100, delay=0.05):
        """Collects Wikipedia section titles until reaching the target count."""

        self.processor = TextProcessor(processor_config)

        num = 0
        row_data_bucket_name = 'raw-' + self.bucket_name
        while num < dataset_size:
            page_title = self.get_random_wikipedia_title()
            sentences = self.get_sentences(page_title)
            for text in sentences:
                file_name = f'title_{num}.txt'
                save_fileobj_to_s3(text, file_name, row_data_bucket_name, prefix='texts')
                num += 1
                if status_every and num % status_every == 0:
                    print(num)
            time.sleep(delay) # Avoid hitting API rate limits
        
        # Postprocessing
        if 'remove_frequent_tokens' in processor_config:
            self.processor.calc_probas()
            self.processor.remove_frequent_tokens(row_data_bucket_name, self.bucket_name)


class AsyncWikiIterator:

    def __init__(self, processor, dataset_size=10000):
        self.WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
        self.dataset_size = dataset_size
        self.ind = 0
        self.processor = processor

    async def get_random_wikipedia_title(self):
        """Fetches a random Wikipedia page title."""
        params = {
            "action": "query",
            "list": "random",
            "rnnamespace": 0, # Only main articles (not Talk, User, etc.)
            "format": "json"
        }
        response = await asyncio.to_thread(requests.get, self.WIKI_API_URL, params=params)
        response_data = response.json()
        return response_data["query"]["random"][0]["title"]
    
    async def get_sections(self, page_title):
        """Fetches section titles from a given Wikipedia page."""
        params = {
            "action": "parse",
            "page": page_title,
            "format": "json",
            "prop": "text"
        }
        response = await asyncio.to_thread(requests.get, self.WIKI_API_URL, params=params)
        if "error" in response:
            return []  # Skip pages with issues
        response_data = response.json()
        html_content = response_data.get("parse", {}).get("text", {}).get("*", "")

        soup = BeautifulSoup(html_content, "html.parser")
        sentences = self.processor(soup)
        
        return sentences

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.ind < self.dataset_size:
            page_title = await self.get_random_wikipedia_title()
            sections = await self.get_sections(page_title)
            self.ind += len(sections)
        else:
            raise StopAsyncIteration
        return sections


class AsyncWikiParser:

    def __init__(self, output_path):
        self.output_path = output_path
        self.counter = 0
        self.lock = asyncio.Lock()
        self.processor = TextProcessor()

    async def write_section(self, sections_set, status_every, delay, semaphore):
        async with semaphore:
            for title in sections_set:
                async with self.lock:
                    with open(os.path.join(self.output_path, f'title_{self.counter}.txt'), 'w', encoding='utf-8') as f:
                        f.write(title)
                    self.counter += 1
                if status_every and self.counter % status_every == 0:
                    print(self.counter)
            await asyncio.sleep(delay)


    async def __call__(self, dataset_size=10000, status_every=100, delay=0.05, num_concurrent=10):
        """Collects Wikipedia section titles until reaching the target count."""
        os.makedirs(self.output_path, exist_ok=True)

        tasks = []
        semaphore = asyncio.Semaphore(num_concurrent)
        async for sections_set in AsyncWikiIterator(processor=self.processor, dataset_size=dataset_size):
            task = asyncio.create_task(self.write_section(sections_set, status_every, delay, semaphore))
            tasks.append(task)

        # Postprocessing
        self.processor.calc_probas()
        self.processor.remove_frequent_tokens(self.output_path)
        
        await asyncio.gather(*tasks)


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
