import pytest


@pytest.fixture
def processor_config():
    processor_config = {
        'remove_section_headers': {},
        'remove_non_ascii_symbols': {},
        'remove_references': {},
        'remove_latex': {},
        'strip_sentences': {},
        'remove_short_sentences': {'min_len': 3},
        'remove_frequent_tokens': {},
    }
    return processor_config