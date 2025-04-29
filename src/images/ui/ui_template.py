import streamlit as st
import os
from PIL import Image, ImageDraw


def draw_yolo_bbox(image, yolo_bbox, outline_color="red", width=2):
    """Draw box on image"""

    # Parse the string into floats
    parts = list(map(float, yolo_bbox.strip().split()))
    
    _, x_center, y_center, w, h = parts
    img_w, img_h = image.size

    # Convert relative coords to absolute pixel coords
    x_center *= img_w
    y_center *= img_h
    w *= img_w
    h *= img_h

    x0 = int(x_center - w / 2)
    y0 = int(y_center - h / 2)
    x1 = int(x_center + w / 2)
    y1 = int(y_center + h / 2)

    # Draw the rectangle
    image_with_box = image.copy()
    draw = ImageDraw.Draw(image_with_box)
    draw.rectangle([x0, y0, x1, y1], outline=outline_color, width=width)
    
    return image_with_box


def get_images_and_boxes(images_path, boxes_path):
    """Load all images and bboxes file paths"""
    image_files = sorted([os.path.join(images_path, img) for img in os.listdir(images_path)])
    if boxes_path != 'None':
        boxes_files = sorted([os.path.join(boxes_path, box) for box in os.listdir(boxes_path)])
    else:
        boxes_files = None
    return image_files, boxes_files


if __name__ == '__main__':

    image_files, boxes_files = get_images_and_boxes('${images_path_placeholder}', '${boxes_path_placeholder}')

    st.set_page_config(layout="wide")
    st.title("Dataset Gallery")
    cols_per_row = st.slider("Images per row", 1, 10, 5)

    # Show images in a grid
    for i in range(0, len(image_files), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(image_files):

                # Read image and box
                img = Image.open(image_files[i + j])
                if boxes_files:
                    with open(boxes_files[i + j], 'r') as f:
                        box = f.read()
                    img = draw_yolo_bbox(img, box)

                # Add image to streamlit
                cols[j].image(img, use_container_width=True, caption=os.path.basename(image_files[i + j]))
