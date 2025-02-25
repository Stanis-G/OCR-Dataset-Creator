import os
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import random
from jinja2 import Environment, FileSystemLoader


class HTMLCreator:
    """Wrap text with html pages"""
    
    def __init__(self, input_path, output_path):
        self.env = Environment(
            loader=FileSystemLoader('src/layouts/templates')
        )
        self.input_path = input_path
        self.output_path = output_path

    def __call__(self, fonts, text_colors, background_images, background_colors, font_size, top, left, start_num=0):
        """
        Generates htmls for text lines in self.output_path

        self.fonts : list of str
            A list of font names to randomly choose from.
        self.text_colors : list of str
            A list of text colors in RGB or Hex format or named colors.
        self.background_images : list of str
            A list of file paths to background images that can be randomly selected.
        self.background_colors : list of str
            A list of background colors for the text, in RGB or Hex format or named colors.
        self.font_size : tuple of int (min, max)
            A range specifying the minimum and maximum font sizes in pixels.
        self.top : tuple of float (min, max)
            A range specifying the relative vertical position of the text in percentage.
        self.left : tuple of float (min, max)
            A range specifying the relative horizontal position of the text in percentage.
        """
        
        os.makedirs(self.output_path, exist_ok=True)

        template = self.env.get_template('base.html')
        for num in range(len(os.listdir(self.input_path))):

            filepath = os.path.join(self.input_path, f'title_{num+start_num}.txt')
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()

            is_bg_image = random.randint(0, 1)
            bg_image = random.choice(background_images) if is_bg_image else ""
            bg_color = random.choice(background_colors)

            html_page = template.render(
                text=text,
                text_color=random.choice(text_colors),
                bg_image=bg_image,
                bg_color=bg_color,
                font=random.choice(fonts),
                font_size=random.randint(*font_size),
                top=random.randint(*top),
                left=random.randint(*left),
            )

            with open(os.path.join(self.output_path, f'page_{num+start_num}.html'), 'w', encoding='utf-8') as f:
                f.write(html_page)
