import sys
from tqdm import tqdm
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from jinja2 import Environment, FileSystemLoader
from layouts.layouts_utils import HTMLProcessor


class HTMLCreator:
    """Wrap text with html pages"""
    
    def __init__(self, storage, subdir='pages'):
        self.storage = storage
        self.subdir = subdir
        self.env = Environment(
            loader=FileSystemLoader('src/layouts/templates')
        )


    def __call__(self, processor_config, texts_subdir):

        self.processor = HTMLProcessor(processor_config)

        template = self.env.get_template('base.html')
        for file_name in tqdm(self.storage.read_all(texts_subdir)):

            num = int(file_name.split('_')[1].split('.')[0])
            page_name = f'page_{num}.html'

            if self.storage.check_file_exists(page_name, self.subdir):
                continue
            text = self.storage.read_file(file_name, texts_subdir, file_type='text')

            html_params = self.processor()
            html_page = template.render(text=text, **html_params)

            # Save page
            self.storage.save_file(html_page, page_name, self.subdir)
