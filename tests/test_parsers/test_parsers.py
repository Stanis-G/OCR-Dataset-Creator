import pytest
from bs4 import BeautifulSoup
from utils.storage import LocalStorage
from parsers.parsers import WikiParser


def test_get_random_wikipedia_title_and_get_sentences():
    parser = WikiParser(storage=LocalStorage('test_storage'))
    title = parser.get_random_wikipedia_title()
    soup = parser.get_soup(title)
    assert isinstance(title, str)
    assert isinstance(soup, BeautifulSoup)
