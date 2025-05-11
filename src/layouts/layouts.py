import copy
import sys
from tqdm import tqdm
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from jinja2 import Environment, FileSystemLoader
from layouts.layouts_utils import HTMLProcessor
from utils.utils import DataCreator, DatasetFactory


class HTMLCreator(DataCreator):
    """Wrap text with html pages"""
    
    def __init__(self, storage_type, storage_params, subdir='pages'):
        super().__init__(storage_type, storage_params, subdir)


    def process(self, file_names, subdir, input_data_subdir, processor_config, storage_type, storage_params, chunk_num, **kwargs):
        storage_cls = DatasetFactory.get_storage(storage_type)
        storage_params_copy = copy.deepcopy(storage_params)
        storage = storage_cls(**storage_params_copy)
        env = Environment(
            loader=FileSystemLoader('src/layouts/templates')
        )
        processor = HTMLProcessor(processor_config)

        template = env.get_template('base.html')
        for file_name in tqdm(file_names, position=chunk_num, desc=f'Process {chunk_num}'):

            # Get text file to place into template
            text = storage.read_file(file_name, input_data_subdir, file_type='text')

            # Render template
            html_params = processor({})
            html_page = template.render(text=text, **html_params)

            # Save page
            num = int(file_name.split('_')[1].split('.')[0])
            page_name = f'page_{num}.html'
            storage.save_file(html_page, page_name, subdir)
