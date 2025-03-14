class OCRDataset:
    
    def __init__(
            self,
            driver_path,
            parser: callable,
            html_creator: callable,
            image_creator: callable,
            bucket_name='ocr_dataset',
        ):
        self.bucket_name = bucket_name
        self.parser = parser(bucket_name=bucket_name)
        self.html_creator = html_creator(bucket_name=bucket_name)
        self.image_creator = image_creator(bucket_name=bucket_name, driver_path=driver_path)


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
            status_every=status_every,
        )
        self.image_creator(
            processor_config=image_processor_config,
            status_every=status_every,
        )
