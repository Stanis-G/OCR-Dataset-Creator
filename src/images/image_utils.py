import cv2
from io import BytesIO
import numpy as np
import random
from PIL import Image


class ImageProcessor:

    def __init__(self, config):
        self.config = config
        self.methods = {
            'add_glare': self.add_glare,
            'add_random_glare': self.add_random_glare,
            'blur': self.blur,
            'random_blur': self.random_blur,
            'random_resize': self.random_resize
        }

    
    def __call__(self, img):
        img = Image.open(BytesIO(img))
        img = np.array(img)
        for method_name, params in self.config.items():
            if method_name in self.methods:
                img = self.methods[method_name](img, **params)
            else:
                raise ValueError(f"Unknown processing method: {method_name}")
        img = Image.fromarray(img)
        return img


    def add_glare(self, img, center=(0.5, 0.5), glare_relative_radius=0.3, glare_intensity=0.4, blur_strength=121):
        # Create black-white circle mask of specified size
        glare = np.zeros_like(img)
        radius = int(min(img.shape[:2]) * glare_relative_radius)
        center = (int(center[0] * img.shape[0]), int(center[1] * img.shape[1]))

        cv2.circle(glare, center, radius, (255, 255, 255), -1)

        # Blur the mask
        kernel = (blur_strength, blur_strength)
        glare = cv2.GaussianBlur(glare, kernel, 0)

        # Sum up original image with mask
        blended = cv2.addWeighted(img, 1, glare, glare_intensity, 0)
        return blended


    def add_random_glare(
        self,
        img,
        center_range=(0, 1),
        glare_relative_radius_range=(0.1, 0.5),
        glare_intensity_range=(0.1, 0.6),
        blur_strength_range=(80, 200),
    ):

        if random.randint(0, 1):
            center = (random.uniform(*center_range), random.uniform(*center_range))
            glare_relative_radius = random.uniform(*glare_relative_radius_range)
            glare_intensity = random.uniform(*glare_intensity_range)
            # glare_intensity multiplier regulates blur in respect to brightness (so there will be no suns in images)
            blur_strength = int(random.randint(*blur_strength_range) * (1 + glare_intensity))
            if blur_strength % 2 == 0:
                blur_strength += 1
            return self.add_glare(img, center, glare_relative_radius, glare_intensity, blur_strength)
        return img


    def blur(self, img, blur_type='gaussian', ksize=3, **blur_args):

        if blur_type == 'avg':
            if isinstance(ksize, int):
                ksize = (ksize, ksize)
            blur_img = cv2.blur(img, ksize, **blur_args)
        elif blur_type == 'median':
            if isinstance(ksize, (list, tuple)):
                ksize = ksize[0]
            if ksize % 2 == 0:
                ksize += 1
            blur_img = cv2.medianBlur(img, ksize, **blur_args)
        elif blur_type == 'gaussian':
            if isinstance(ksize, int):
                ksize = (ksize, ksize)
            if ksize[0] % 2 == 0:
                ksize = (ksize[0] + 1, ksize[1] + 1)
            if 'sigmaX' not in blur_args:
                blur_args['sigmaX'] = 0
            blur_img = cv2.GaussianBlur(img, ksize, **blur_args)
        else:
            raise ValueError(f"Value '{blur_type}' for 'blur_type' is not valid")
        return blur_img


    def random_blur(self, img, blur_type_values=('avg', 'median', 'gaussian'), ksize_range=(3, 8)):
        if random.randint(0, 1):
            blur_type = random.choice(blur_type_values)
            ksize = random.randint(*ksize_range)
            return self.blur(img, blur_type, ksize)
        return img
    

    def random_resize(self, img, width_range, height_range):
        shape_new = random.randint(*width_range), random.randint(*height_range)
        img = Image.fromarray(img)
        img = img.resize(shape_new)
        return np.array(img)
