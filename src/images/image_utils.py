import cv2
from io import BytesIO
import numpy as np
import random
from PIL import Image
from src.utils.utils import BaseProcessor


def get_yolo_bounding_box(coords, canvas_width, canvas_height):
    x_center = (coords['left'] + coords['width'] / 2) / canvas_width
    y_center = (coords['top'] + coords['height'] / 2) / canvas_height
    width = coords['width'] / canvas_width
    height = coords['height'] / canvas_height
    return f"0 {x_center} {y_center} {width} {height}"


class ImageProcessor(BaseProcessor):

    def __init__(self, config):
        super().__init__(config)
        self.methods = {
            'add_glare': self.add_glare,
            'add_random_glare': self.add_random_glare,
            'blur': self.blur,
            'random_blur': self.random_blur,
            'random_resize': self.random_resize,
            'add_gaussian_noise': self.add_gaussian_noise,
            'add_random_gaussian_noise': self.add_random_gaussian_noise,
            'add_impulse_noise': self.add_impulse_noise,
            'add_random_impulse_noise': self.add_random_impulse_noise,
            'add_motion_blur': self.add_motion_blur,
            'add_random_motion_blur': self.add_random_motion_blur,
        }

    
    def __call__(self, img, bytes_like=True):
        if bytes_like:
            img = Image.open(BytesIO(img))
        img = np.array(img)
        img = super().__call__(img)
        img = Image.fromarray(img)
        return img


    def add_glare(self, img, center=(0.5, 0.5), glare_relative_radius=0.3, glare_intensity=0.4, blur_strength=121):

        if blur_strength % 2 == 0:
            blur_strength += 1
        center = [max(0, i) for i in center]
        blur_strength = abs(blur_strength)

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
            # Check values
            center_range = [abs(i) for i in center_range]
            glare_relative_radius_range = [abs(i) for i in glare_relative_radius_range]
            glare_intensity_range = [abs(i) for i in glare_intensity_range]
            blur_strength_range = [abs(i) for i in blur_strength_range]

            # Generate glare params
            center = (random.uniform(*center_range), random.uniform(*center_range))
            glare_relative_radius = random.uniform(*glare_relative_radius_range)
            glare_intensity = random.uniform(*glare_intensity_range)
            # glare_intensity multiplier regulates blur in respect to brightness (so there will be no suns in images)
            blur_strength = int(random.randint(*blur_strength_range) * (1 + glare_intensity))
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
    

    def random_resize(self, img, width_range=(500, 1500), height_range=(500, 1500)):
        width_range = (min(width_range), max(width_range))
        height_range = (min(height_range), max(height_range))

        shape_new = random.randint(*width_range), random.randint(*height_range)
        img = Image.fromarray(img)
        img = img.resize(shape_new)
        return np.array(img)
    

    def add_gaussian_noise(self, img, mean=0, std=0.1):
        noise = np.random.normal(mean, std, img.shape).astype('uint8')
        img = cv2.add(img, noise)
        return img
    
    
    def add_random_gaussian_noise(self, img, mean_range=(0, 10), std_range=(0, 10)):
        mean = random.uniform(*mean_range)
        std = random.uniform(*std_range)
        img = self.add_gaussian_noise(img, mean, std)
        return img
    

    def add_impulse_noise(self, img, proba=0.01):
        black_mask = (np.random.rand(*img.shape[:2]) < proba) # mask of pixels to become black
        white_mask = (np.random.rand(*img.shape[:2]) < proba) # mask of pixels to become white
        img[black_mask] = [0, 0, 0]
        img[white_mask] = [255, 255, 255]
        return img
    

    def add_random_impulse_noise(self, img, proba_range=(0, 0.05)):
        proba = random.uniform(*proba_range)
        img = self.add_impulse_noise(img, proba)
        return img
    

    def add_motion_blur(self, img, kernel_size=15, angle=0):
        image_np = np.array(img)

        # Create the motion blur kernel
        kernel = np.zeros((kernel_size, kernel_size))
        kernel[int((kernel_size - 1) / 2), :] = np.ones(kernel_size)
        rotation_matrix = cv2.getRotationMatrix2D((kernel_size / 2 - 0.5, kernel_size / 2 - 0.5), angle, 1)
        kernel = cv2.warpAffine(kernel, rotation_matrix, (kernel_size, kernel_size))
        kernel = kernel / np.sum(kernel)

        # Apply kernel to each channel
        img_blurred = np.zeros_like(image_np)
        for i in range(3):
            img_blurred[:, :, i] = cv2.filter2D(image_np[:, :, i], -1, kernel)

        return img_blurred
    

    def add_random_motion_blur(self, img, kernel_size_range=(1, 20), angle_range=(0, 90)):
        kernel_size = random.randint(*kernel_size_range)
        angle = random.randint(*angle_range)
        img = self.add_motion_blur(img, kernel_size, angle)
        return img
