import pytest
from bs4 import BeautifulSoup
from src.utils.storage import LocalStorage
from src.parsers.parsers import WikiParser


def test_get_random_wikipedia_title_and_get_sentences():
    parser = WikiParser(
        storage_cls=LocalStorage,
        storage_params={'dataset_name': 'test_storage'},
        subdir='texts'
    )
    title = parser.get_random_wikipedia_title()
    soup = parser.get_soup(title)
    assert isinstance(title, str)
    assert isinstance(soup, BeautifulSoup)
