from itertools import permutations
import pytest
import random

from parsers.parsers import WikiParser


@pytest.fixture
def get_soup(local_storage):

    storage = local_storage
    parser = WikiParser(storage=storage, subdir='texts')
    
    page_title = parser.get_random_wikipedia_title()
    soup = parser.get_soup(page_title)
    return soup


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
