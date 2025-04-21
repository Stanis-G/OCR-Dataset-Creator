from src.utils.storage import Storage


class OCRDataset:
    
    def __init__(
            self,
            driver_path,
            parser: callable,
            html_creator: callable,
            image_creator: callable,
            storage: Storage,
            texts_subdir='texts',
            pages_subdir='pages',
            images_subdir='images',
            bbox_subdir='boxes',
        ):
        self.parser = parser(storage=storage, subdir=texts_subdir)
        self.html_creator = html_creator(storage=storage, subdir=pages_subdir)
        self.image_creator = image_creator(storage=storage, driver_path=driver_path, subdir=images_subdir, bbox_subdir=bbox_subdir)

        self.texts_subdir = texts_subdir
        self.pages_subdir = pages_subdir
        self.images_subdir = images_subdir


    def __call__(self, text_processor_config, html_processor_config, image_processor_config, dataset_size=1000, delay=0.05):
        
        # Run dataset parsing and processing
        self.parser(
            processor_config=text_processor_config,
            dataset_size=dataset_size,
            delay=delay,
        )
        self.html_creator(
            processor_config=html_processor_config,
            texts_subdir=self.texts_subdir,
        )
        self.image_creator(
            processor_config=image_processor_config,
            pages_subdir=self.pages_subdir,
        )
