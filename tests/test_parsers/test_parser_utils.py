from parsers.parser_utils import TextProcessor


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
