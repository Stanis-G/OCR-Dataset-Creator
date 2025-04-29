# Description
The repository is an attempt to automate the process of OCR (Optical Character Recognition) dataset creation. There are tools to extract raw text data from websites, setting visual layouts and making images. It allows to gather large datasets in no time, although the gathered data is an imitation of real world data. Efficiency of OCR models, trained on this data, may suffer because of the fact.

__1. Parsers__
src/parcers/parcers.py contains classes to parse data from various sources.
src/parcers/parser_utils.py containts class for text processing

__2. Layouts__
src/layouts/layouts.py contains a class, making html using passed text and template. Add some randomness like colors, text position...

__3. Images__
src/images/images.py has a class for making screenshots of htmls
src/images/image_utils.py has functions to preprocess images

__Datasets__
src/dataset/dataset.py has a class to combine parser, layouts and images and properly handle dataset directory structure

__Examples__
Contains examples of using for different parsers. Some examples are inconsistent for now

# Considerations
The considerations include:
1. Add tests for Dataset and DataCreator subclasses
2. Refine async classes
3. Extend processing functions
4. Add support for more tokenizers
5. Add multiple text blocks in one template
6. Add more details into html template (lines, frames, tables, text rotation...)
7. Get rid of driver
8. Create storage for background images
9. Add more examples of use
10. Fix out of image text location
11. Add support of streamlit ui for S3 storage
