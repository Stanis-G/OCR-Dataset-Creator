import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from jinja2 import Environment, FileSystemLoader
from layouts.layouts_utils import HTMLProcessor
from utils.utils import save_fileobj_to_s3, read_file_from_s3, list_objects_in_bucket


class HTMLCreator:
    """Wrap text with html pages"""
    
    def __init__(self, bucket_name):
        self.env = Environment(
            loader=FileSystemLoader('src/layouts/templates')
        )
        self.bucket_name = bucket_name

    def __call__(self, processor_config, status_every=1000):

        self.processor = HTMLProcessor(processor_config)

        template = self.env.get_template('base.html')
        for i, file_name in enumerate(list_objects_in_bucket(self.bucket_name, prefix='texts', page_size=1000)):

            num = int(file_name.split('_')[1].split('.')[0])
            text = read_file_from_s3(file_name, self.bucket_name)

            html_params = self.processor()
            html_page = template.render(text=text, **html_params)

            page_name = f'page_{num}.html'
            save_fileobj_to_s3(html_page, page_name, self.bucket_name, prefix='pages')

            if status_every and i % status_every == 0:
                print(i)
