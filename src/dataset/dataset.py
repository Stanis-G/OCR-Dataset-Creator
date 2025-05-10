from src.utils.storage import LocalStorage, S3Storage
from src.utils.utils import DataCreator, generate_ui_script


class DatasetFactory:

    @classmethod
    def get_storage(self, storage_type='local', storage_params={}):
        classes = {'local': LocalStorage, 'S3': S3Storage}
        cls = classes[storage_type]
        return cls(**storage_params)


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
        self.storage = DatasetFactory.get_storage(storage_type, storage_params)
        self.parser = parser(storage=self.storage, subdir=texts_subdir)
        self.html_creator = html_creator(storage=self.storage, subdir=pages_subdir)
        self.image_creator = image_creator(storage=self.storage, driver_path=driver_path, subdir=images_subdir, bbox_subdir=bbox_subdir)

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


    def __call__(self, text_processor_config, html_processor_config, image_processor_config, dataset_size=1000, delay=0.05):

        start_index_texts, start_index_pages, start_index_images = self.get_start_indeces(dataset_size)
        
        # Run dataset parsing and processing
        self.parser(
            processor_config=text_processor_config,
            dataset_size=dataset_size,
            delay=delay,
            start_index=start_index_texts,
        )
        self.html_creator(
            processor_config=html_processor_config,
            texts_subdir=self.texts_subdir,
            start_index=start_index_pages,
        )
        self.image_creator(
            processor_config=image_processor_config,
            pages_subdir=self.pages_subdir,
            start_index=start_index_images,
        )

        # Generate py script to run streamlit UI
        ui_script = generate_ui_script(
            images_path=self.images_subdir,
            boxes_path=self.bbox_subdir,
            texts_path=self.texts_subdir,
        )
        self.storage.save_file(ui_script, 'ui.py')


class DatasetFactory:

    @classmethod
    def get_storage(self, storage_type='local'):
        classes = {'local': LocalStorage, 'S3': S3Storage}
        return classes[storage_type]


class ParallelOCRDataset:
    
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
        self.storage = storage_cls(**storage_params)
        self.parser = parser(
            storage_cls=storage_cls,
            storage_params=storage_params,
            subdir=texts_subdir,
        )
        self.html_creator = html_creator(
            storage_cls=storage_cls,
            storage_params=storage_params,
            subdir=pages_subdir,
        )
        self.image_creator = image_creator(
            storage_cls=storage_cls,
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
        
        # Run dataset parsing and processing
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

        html_process_params = {
            'processor_config': html_processor_config,
        }
        self.html_creator(
            process_params=html_process_params,
            input_data_subdir=self.texts_subdir,
            start_index=start_index_pages,
            num_processes=num_processes,
        )

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
