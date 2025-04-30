import streamlit as st
import os
from pathlib import Path
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


def get_images_and_boxes(images_path, boxes_path, texts_path):
    """Load all images and bboxes file paths"""
    image_files = sorted([os.path.join(images_path, img) for img in os.listdir(images_path)])
    if os.path.exists(boxes_path):
        boxes_files = sorted([os.path.join(boxes_path, box) for box in os.listdir(boxes_path)])
    else:
        boxes_files = None
    if os.path.exists(texts_path):
        texts_files = sorted([os.path.join(texts_path, text) for text in os.listdir(texts_path)])
    else:
        texts_files = None
    return image_files, boxes_files, texts_files


if __name__ == '__main__':

    script_dir = Path(__file__).resolve().parent
    images_path = os.path.join(script_dir, '${images_path_placeholder}')
    boxes_path = os.path.join(script_dir, '${boxes_path_placeholder}')
    texts_path = os.path.join(script_dir, '${texts_path_placeholder}')

    image_files, boxes_files, texts_files = get_images_and_boxes(images_path, boxes_path, texts_path)

    st.set_page_config(layout="wide")
    st.title("Dataset Gallery")
    cols_per_row = st.slider("Images per row", 1, 10, 5)
    show_texts = st.checkbox("Show texts", value=False)

    # Show images in a grid
    for i in range(0, len(image_files), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):

            idx = i + j
            if idx < len(image_files):

                # Read image and box
                img = Image.open(image_files[idx])
                if boxes_files:
                    with open(boxes_files[idx], 'r') as f:
                        box = f.read()
                    img = draw_yolo_bbox(img, box)

                with cols[j]:
                    if show_texts and texts_files:
                        with open(texts_files[idx], 'r', encoding='utf-8') as tf:
                            text = tf.read()
                        st.text_area("Text", text, height=100, disabled=True, label_visibility='hidden')
                    st.image(img, use_container_width=True, caption=os.path.basename(image_files[idx]))
