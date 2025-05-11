import copy

from src.utils.utils import DataCreator, DatasetFactory, generate_ui_script


class OCRDataset:
    
    def __init__(
            self,
            driver_path,
            parser: DataCreator,
            html_creator: DataCreator,
            image_creator: DataCreator,
            storage_type: str,
            storage_params: dict,
            texts_subdir='texts',
            pages_subdir='pages',
            images_subdir='images',
            bbox_subdir='labels',
        ):
        self.dataset_name = storage_params.get('dataset_name')
        storage_cls = DatasetFactory.get_storage(storage_type)
        storage_params_copy = copy.deepcopy(storage_params)
        self.storage = storage_cls(**storage_params_copy)
        self.parser = parser(
            storage_type=storage_type,
            storage_params=storage_params,
            subdir=texts_subdir,
        )
        self.html_creator = html_creator(
            storage_type=storage_type,
            storage_params=storage_params,
            subdir=pages_subdir,
        )
        self.image_creator = image_creator(
            storage_type=storage_type,
            storage_params=storage_params,
            driver_path=driver_path,
            subdir=images_subdir,
            bbox_subdir=bbox_subdir,
        )

        self.texts_subdir = texts_subdir
        self.pages_subdir = pages_subdir
        self.images_subdir = images_subdir
        self.bbox_subdir = bbox_subdir


    def get_start_indeces(self, dataset_size=1000):
        texts = self.storage.read_all(self.texts_subdir)
        pages = self.storage.read_all(self.pages_subdir)
        images = self.storage.read_all(self.images_subdir)
        start_index_texts = min(len(texts), dataset_size)
        start_index_pages = min(len(pages), dataset_size)
        start_index_images = min(len(images), dataset_size)
        return start_index_texts, start_index_pages, start_index_images


    def __call__(self, text_processor_config, html_processor_config, image_processor_config, dataset_size=1000, delay=0.05, num_processes=5):

        start_index_texts, start_index_pages, start_index_images = self.get_start_indeces(dataset_size)
        
        # Run dataset parsing
        text_process_params = {
            'processor_config': text_processor_config,
            'delay': delay,
        }
        self.parser(
            process_params=text_process_params,
            dataset_size=dataset_size,
            start_index=start_index_texts,
            num_processes=num_processes,
        )

        # Put parsed texts into html template
        html_process_params = {
            'processor_config': html_processor_config,
        }
        self.html_creator(
            process_params=html_process_params,
            input_data_subdir=self.texts_subdir,
            start_index=start_index_pages,
            num_processes=num_processes,
        )

        # Make screenshots of html pages
        image_process_params = {
            'processor_config': image_processor_config,
            'bbox_subdir': self.bbox_subdir,
        }
        self.image_creator(
            process_params=image_process_params,
            input_data_subdir=self.pages_subdir,
            start_index=start_index_images,
            num_processes=num_processes,
        )

        # Generate py script to run streamlit UI
        ui_script = generate_ui_script(
            images_path=self.images_subdir,
            boxes_path=self.bbox_subdir,
            texts_path=self.texts_subdir,
        )
        self.storage.save_file(ui_script, 'ui.py')
