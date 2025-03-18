class OCRDataset:
    
    def __init__(
            self,
            driver_path,
            parser: callable,
            html_creator: callable,
            image_creator: callable,
            bucket_name='ocr-dataset',
            texts_prefix='texts',
            pages_prefix='pages',
            images_prefix='images',
        ):
        self.bucket_name = bucket_name
        self.parser = parser(bucket_name=bucket_name, prefix=texts_prefix)
        self.html_creator = html_creator(bucket_name=bucket_name, prefix=pages_prefix)
        self.image_creator = image_creator(bucket_name=bucket_name, driver_path=driver_path, prefix=images_prefix)
        self.texts_prefix = texts_prefix
        self.pages_prefix = pages_prefix
        self.images_prefix = images_prefix


    def __call__(self, text_processor_config, html_processor_config, image_processor_config, dataset_size=1000, status_every=1000, delay=0.05):
        
        # Run dataset parsing and processing
        self.parser(
            processor_config=text_processor_config,
            dataset_size=dataset_size,
            status_every=status_every,
            delay=delay,
        )
        self.html_creator(
            processor_config=html_processor_config,
            text_prefix=self.texts_prefix,
            status_every=status_every,
        )
        self.image_creator(
            processor_config=image_processor_config,
            pages_prefix=self.pages_prefix,
            status_every=status_every,
        )
