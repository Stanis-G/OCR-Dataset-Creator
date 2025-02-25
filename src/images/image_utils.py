import cv2
import numpy as np
import random


def add_glare(img, center=(0.5, 0.5), glare_relative_radius=0.3, glare_intensity=0.4, blur_strength=121):
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
        return add_glare(img, center, glare_relative_radius, glare_intensity, blur_strength)
    return img


def blur(img, blur_type='gaussian', ksize=3, **blur_args):

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


def random_blur(img, blur_type_values=('avg', 'median', 'gaussian'), ksize_range=(3, 8)):

    if random.randint(0, 1):
        blur_type = random.choice(blur_type_values)
        ksize = random.randint(*ksize_range)
        return blur(img, blur_type, ksize)
    return img
