from layouts.layouts_utils import HTMLProcessor


def test_HTMLProcessor_call_without_params(html_processor_config_without_params):
    """Test HTMLProcessor.__call__ with all awailable methods with no params"""
    config = html_processor_config_without_params
    processor = HTMLProcessor(config=config)

    params = processor({})

    assert isinstance(params, dict)
    assert params


def test_HTMLProcessor_call_with_params(html_processor_config_with_params):
    """Test HTMLProcessor.__call__ with all awailable methods with specified params"""
    config = html_processor_config_with_params
    processor = HTMLProcessor(config=config)

    params = processor({})

    assert isinstance(params, dict)
    assert params