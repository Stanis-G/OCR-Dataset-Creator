import logging
import os
import shutil
from src.layouts.htmls import HTMLCreator
from src.images.images import ImageCreator


class OCRDataset:
    
    def __init__(
            self,
            parser: callable,
            html_creator: HTMLCreator,
            image_creator: ImageCreator,
        ):
        self.parser = parser
        self.html_creator = html_creator
        self.image_creator = image_creator
        self.text_fold = 'texts'
        self.html_fold = 'pages'
        self.images_fold = 'images'


    def __call__(self, output_folder='data', data_exists_handler=None, parser_args={}):

        self.check_data_folder(output_folder)

        data_size = 0
        if os.path.exists(output_folder) and data_exists_handler == 'delete':
            shutil.rmtree(output_folder)
        elif os.path.exists(output_folder) and data_exists_handler == 'complete':
            data_size = len(os.listdir(os.path.join(output_folder, self.text_fold)))
        elif os.path.exists(output_folder) and not data_exists_handler:
            logging.warning("'output_folder' already exists. Please specify 'data_exists_handler'")
            return None

        text_path = os.path.join(output_folder, self.text_fold)
        html_path = os.path.join(output_folder, self.html_fold)
        image_path = os.path.join(output_folder, self.images_fold)
        
        self.parser(
            output_path=text_path,
            start_num=data_size,
            **parser_args,
        ) # create raw dataset in a project folder (locally or url like google docs)
        self.html_creator(
            input_path=text_path,
            output_path=html_path,
            start_num=data_size,
        ) # add text to html
        self.image_creator(
            input_path=html_path,
            output_path=image_path,
            start_num=data_size,
        ) # make screenshot from html and add effects

    
    def check_data_folder(self, data_folder):

        if os.path.exists(data_folder):
            num_texts = len(os.listdir(os.path.join(data_folder, self.text_fold)))
            num_htmls = len(os.listdir(os.path.join(data_folder, self.html_fold)))
            num_images = len(os.listdir(os.path.join(data_folder, self.images_fold)))
            if not num_texts == num_htmls == num_images:
                raise ValueError('Numbers of samples have to be equal in data subfolders')
