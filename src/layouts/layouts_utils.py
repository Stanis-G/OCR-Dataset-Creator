import random


class HTMLProcessor:

    def __init__(self, config):
        self.config = config

    
    def __call__(self):
        is_bg_image = random.randint(0, 1)
        is_text_highlighted = random.randint(0, 1)
        params = dict(
            bg_image=random.choice(self.config['bg_images']) if is_bg_image else "",
            bg_color=random.choice(self.config['bg_colors']),
            text_color=random.choice(self.config['text_colors']),
            font=random.choice(self.config['fonts']),
            font_size=random.randint(*self.config['font_size']),
            top=random.randint(*self.config['top']),
            left=random.randint(*self.config['left']),
            text_highlight_color=random.choice(self.config['text_highlight_colors']) if is_text_highlighted else "",
            highlight_padding_height=random.randint(*self.config['highlight_padding']) if is_text_highlighted else "",
            highlight_padding_width=random.randint(*self.config['highlight_padding']) if is_text_highlighted else "",
            hihglight_rounding=random.randint(*self.config['highlight_rounding']),
        )
        return params
