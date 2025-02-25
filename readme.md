# Description
The repository is an attempt to automate the process of OCR (Optical Character Recognition) dataset creation. There are tools to extract raw text data from websites, setting visual layouts and making images. It allows to gather large datasets in no time, although the gathered data is an imitation of real world data. Efficiency of OCR models, trained on this data, may suffer because of the fact.

__1. Parsers__
src/parcers/parcers.py contains classes to parse data from various sources. Also there is async versions for Wikipedia parser.
src/parcersparser_utils.py containts class for text processing

__2. Layouts__
src/layouts/htmls.py is for a class, making html using passed text and template. Add some randomness like colors, text position...
(not implemented) src/layouts/presentations.py contains a class for putting text into .pptx templates with randomization

__3. Images__
src/images/images.py has a class, making screenshot of html
src/images/image_utils.py has functions to preprocess images

__Datasets__
src/dataset/dataset.py has a class to combine parser, layouts and images and properly handle dataset directory structure

__Examples__
Contains examples of using for different parsers

# Considerations
The code is raw and partially inconsistent for now. The considerations include:
1. Unifying code base
2. Adding tests
3. Extending processing functions
4. Adding cloud storage support
5. Adding multiple text blocks in one template
6. Adding bounding boxes aroung text blocks in images for detection models
