from bs4 import BeautifulSoup
import pytest

from src.parsers.parser_utils import TextProcessor


def test_fully_configured_TextProcessor_call(get_soup, text_processor_config):
    """Test TextProcessor.__call__ with all awailable methods"""
    config = text_processor_config
    processor = TextProcessor(config=config)

    soup = get_soup
    sentences = processor(soup)

    assert isinstance(sentences, list)


def test_zero_and_single_method_TextProcessor_call(get_soup, text_processor_config_single_and_zero):
    """Test TextProcessor.__call__ with empty config and with every available method one by one"""
    config_lst = text_processor_config_single_and_zero

    for config in config_lst:
        processor = TextProcessor(config=config)

        soup = get_soup
        sentences = processor(soup)

        assert isinstance(sentences, list)


def test_remove_section_headers(get_soup):
    processor = TextProcessor(config=None)

    soup = get_soup
    soup = processor.remove_section_headers(soup)

    assert isinstance(soup, BeautifulSoup)


def test_extract_text(get_soup):
    processor = TextProcessor(config=None)

    soup = get_soup
    text = processor.extract_text(soup)

    assert isinstance(text, str)


def test_remove_non_ascii_symbols(get_text):
    processor = TextProcessor(config=None)

    text = get_text
    text_res = processor.remove_non_ascii_symbols(text)

    assert text_res != text


def test_remove_references(get_text):
    processor = TextProcessor(config=None)

    text = get_text
    text_res = processor.remove_references(text)

    assert text_res == text[:-3]


def test_split_into_sentences(get_text):
    processor = TextProcessor(config=None)

    text = get_text
    sentences = processor.split_into_sentences(text)

    assert isinstance(sentences, list)
    assert len(sentences) == 3


def test_remove_latex(get_text):
    processor = TextProcessor(config=None)

    text = get_text
    sentences = processor.split_into_sentences(text)
    sentences_res = processor.remove_latex(sentences)

    assert sentences_res != sentences
    assert len(sentences_res) == 2


def test_strip_sentences(get_sentences):
    processor = TextProcessor(config=None)

    sentences = get_sentences
    sentences = processor.strip_sentences(sentences)

    assert sentences == ['Hi', 'How are you?']


def test_remove_short_sentences(get_sentences):
    processor = TextProcessor(config=None)

    sentences = get_sentences
    sentences = processor.remove_short_sentences(sentences, min_len=4)

    assert sentences == ['How are you? ']


def test_update_token_counts_and_calc_probas(get_sentences):
    processor = TextProcessor(config=None)

    sentences = get_sentences
    sentences_res = processor.update_token_counts(sentences)
    processor.calc_probas()

    assert sentences_res == sentences
    assert processor.token_counts
    assert processor.proba_dct


def test_calc_probas():
    processor = TextProcessor(config=None)

    with pytest.raises(ValueError, match="You must calculate token counts before calculating probas*"):
        processor.calc_probas()
