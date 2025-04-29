import base64
from collections import OrderedDict
import os
import random

from src.utils.utils import BaseProcessor
from src.layouts.config import FONTS, COLORS


class HTMLProcessor(BaseProcessor):

    def __init__(self, config):
        super().__init__(config)
        self.methods = OrderedDict({
            'get_bg_image': self.get_bg_image,
            'get_colors': self.get_colors,
            'get_font': self.get_font,
            'get_text_position': self.get_text_position,
            'get_highlight_params': self.get_highlight_params,
        })

    
    def __call__(self, obj={}):
        return super().__call__(obj)


    def get_bg_image(self, params, bg_images, proba=0.5):
        """Set background image"""
        is_bg_image = random.uniform(0, 1) < proba
        if is_bg_image and bg_images:
            if isinstance(bg_images, str):
                # Treat bg_images like local path to bg images
                bg_name = random.choice(os.listdir(bg_images))
                bg_path = os.path.join(bg_images, bg_name)
                with open(bg_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                bg_image_url = f"data:image/jpeg;base64,{encoded_string}"
            elif isinstance(bg_images, list):
                # If bg_images is a list of urls
                bg_image_url = random.choice(bg_images)
            else:
                raise TypeError('bg_images should be "None", "str" or "list"')
        else:
            bg_image_url = ""

        params['bg_image'] = bg_image_url
        return params


    def get_colors(self, params, colors=COLORS):
        """Set text and background colors"""
        bg_color = random.choice(colors)

        text_color = random.choice(colors)
        while bg_color == text_color:
            text_color = random.choice(colors)

        params['bg_color'] = bg_color
        params['text_color'] = text_color
        return params


    def get_font(self, params, font_size_range=(10, 50), fonts=FONTS):
        """Set font and text size"""
        params['font'] = random.choice(fonts)
        params['font_size'] = random.randint(*font_size_range)
        return params


    def get_text_position(self, params, top_range=(5, 75), left_range=(5, 75)):
        """Set text position in the screen"""
        params['top'] = random.randint(*top_range)
        params['left'] = random.randint(*left_range)
        return params


    def get_highlight_params(self, params, colors=COLORS, proba=0.5, highlight_padding_range=(1, 30), highlight_rounding_range=(1, 15)):
        """Set highlight color, size and rounding"""
        is_text_highlighted = random.uniform(0, 1) < proba
        if is_text_highlighted:
            text_highlight_color = random.choice(colors)
            while text_highlight_color == params['bg_color'] or text_highlight_color == params['text_color']:
                text_highlight_color = random.choice(colors)

            highlight_padding_height=random.randint(*highlight_padding_range)
            highlight_padding_width=random.randint(*highlight_padding_range)
            highlight_rounding=random.randint(*highlight_rounding_range),
        else:
            text_highlight_color = ""
            highlight_padding_height = ""
            highlight_padding_width = ""
            highlight_rounding = ""

        params['text_highlight_color'] = text_highlight_color
        params['highlight_padding_height'] = highlight_padding_height
        params['highlight_padding_width'] = highlight_padding_width
        params['highlight_rounding'] = highlight_rounding
        return params
