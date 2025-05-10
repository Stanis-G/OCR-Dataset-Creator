# Description
The repository is an attempt to automate the process of OCR (Optical Character Recognition) dataset creation. There are tools to extract raw text data from websites, setting visual layouts and making images. It allows to gather large datasets in no time, although the gathered data is an imitation of real world data. Efficiency of OCR models, trained on this data, may suffer because of the fact.

__1. Parsers__

Parsers package has tools to gather text data from various sources. Text data undergoes some preprocessing steps and gets divided into smaller pieces, fitting into one image. Unified interface will be provided in the future, so one will be able to create their own parsers.

__2. Layouts__

Layouts package is meant to put parsed text into html template. Processing functions at this step allow some randomness regarding to text size, position in a canvas, color, background images and many other, making dataset diverse.

__3. Images__

Images package is about making screenshots of html files from previous step and then processing it via some visual tools, which can be noises of several types, blur, glare and image resize. These tools also have some randomness.
Besides, images package has functionality of making bounding boxes around the text in image. These bboxes are saved in YOLO format so they can be used to train YOLO model for detection tasks.

__Datasets__

Dataset package combines parsers, layouts and images. It handles dataset directory or S3 bucket structure and generates streamlit ui script, displaying all images with drawn bboxes and corresponding parsed texts. It is useful to see your data and check it for problems, so you can change processing settings in previous steps and generate a new dataset.
To open streamlit ui after you have generated dataset, just run `streamlit run <dataset_folder>/ui.py` from env with streamlit installed. If you use S3 stored dataset, you need to download it first.

__Examples__

Contains examples of use for different parsers. Some examples are inconsistent for now

# Considerations
The considerations include:
1. Add tests for Dataset and DataCreator subclasses
2. Refine async classes
3. Extend processing functions (image compression, dust, scratches, smudges, affine and projective transformations)
4. Add support for more tokenizers
5. Add multiple text blocks in one template
6. Add more details into html template (lines, frames, tables, text rotation...)
7. Get rid of driver
8. Create storage for background images
9. Add more examples of use
10. Fix out of image text location
11. Make unified interface for parsers
12. Deprecate non parallel classes (change test to work with parallel classes, add data postprocessing mechanism)
