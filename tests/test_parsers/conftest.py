from itertools import permutations
import pytest
import random

from src.parsers.parsers import WikiParser


@pytest.fixture
def get_soup(local_storage):
    storage_cls, storage_params = local_storage
    parser = WikiParser(
        storage_cls=storage_cls,
        storage_params=storage_params,
        subdir='texts',
    )

    page_title = parser.get_random_wikipedia_title()
    soup = parser.get_soup(page_title)
    return soup


@pytest.fixture
def get_text():
    return """{\\displaystile Zoë enjoys hiking in the Swiss Alps.
            She said, 'C'était une expérience inoubliable!'
            Later, she shared her journey online: '¡Gracias a todos por el apoyo!'[5]"""


@pytest.fixture
def get_sentences():
    return [' Hi', 'How are you? ']


@pytest.fixture
def text_processor_config():
    config = {
        'remove_section_headers': {},
        'remove_non_ascii_symbols': {},
        'remove_references': {},
        'remove_latex': {},
        'strip_sentences': {},
        'remove_short_sentences': {'min_len': 3},
        'remove_frequent_tokens': {},
    }
    return config


@pytest.fixture
def text_processor_config_single_and_zero(text_processor_config):
    config = text_processor_config
    all_perms = list(permutations(config.items(), 1))
    config_lst = [dict(conf) for conf in all_perms]
    return config_lst



@pytest.fixture
def text_processor_config_random(text_processor_config, r, num_choices):
    config = text_processor_config
    all_perms = list(permutations(config.items(), r))
    config_lst = [dict(random.choice(all_perms)) for _ in range(num_choices)]
    return config_lst
