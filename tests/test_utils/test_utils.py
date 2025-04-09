import pytest

from utils.storage import LocalStorage
from utils.utils import DataCreator


@pytest.mark.parametrize("subdir,storage", [
    ('texts', LocalStorage('test-storage')),
    ('text_dir', LocalStorage('test-storage')),
    (None, LocalStorage('test-storage')),
    ('text_dir', None),
])
def test_DataCreator_init(subdir, storage):

    if not subdir or not storage:
        with pytest.raises(TypeError):
            DataCreator(storage=storage, subdir=subdir)
    else:
        parser = DataCreator(storage=storage, subdir=subdir)
        assert hasattr(parser, 'subdir')
        assert hasattr(parser, 'storage')
