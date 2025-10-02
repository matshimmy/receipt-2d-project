import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import random
from typing import Tuple, Optional


class AugmentationPipeline:
    def __init__(self,
                 rotation_range: Tuple[float, float] = (-3, 3),
                 noise_level: Tuple[float, float] = (0, 0.01),
                 blur_range: Tuple[float, float] = (0, 0.25),  # Further reduced for subtler blur
                 brightness_range: Tuple[float, float] = (0.85, 1.15),
                 contrast_range: Tuple[float, float] = (0.9, 1.1),
                 perspective_distortion: float = 0.05,  # Reduced from 0.1
                 crumple_intensity: float = 0.02):

        self.rotation_range = rotation_range
        self.noise_level = noise_level
        self.blur_range = blur_range
        self.brightness_range = brightness_range
        self.contrast_range = contrast_range
        self.perspective_distortion = perspective_distortion
        self.crumple_intensity = crumple_intensity

    def apply(self, image: Image.Image, augmentations: Optional[list] = None) -> Image.Image:
        if augmentations is None:
            augmentations = ["rotation", "noise", "blur", "brightness", "contrast", "perspective"]

        # Convert to numpy for some operations
        img_array = np.array(image)

        if "rotation" in augmentations:
            image = self._apply_rotation(image)

        if "perspective" in augmentations:
            img_array = self._apply_perspective(img_array)
            image = Image.fromarray(img_array)

        if "noise" in augmentations:
            img_array = np.array(image)
            img_array = self._add_noise(img_array)
            image = Image.fromarray(img_array)

        if "blur" in augmentations:
            image = self._apply_blur(image)

        if "brightness" in augmentations:
            image = self._adjust_brightness(image)

        if "contrast" in augmentations:
            image = self._adjust_contrast(image)

        if "crumple" in augmentations:
            img_array = np.array(image)
            img_array = self._add_crumple_effect(img_array)
            image = Image.fromarray(img_array)

        if "shadow" in augmentations:
            image = self._add_shadow(image)

        return image

    def _apply_rotation(self, image: Image.Image) -> Image.Image:
        angle = random.uniform(*self.rotation_range)

        # Use high-quality resampling for smooth rotation
        # First, upscale the image for better quality
        original_size = image.size
        upscale_factor = 2
        large_size = (image.width * upscale_factor, image.height * upscale_factor)

        # Upscale with high-quality resampling
        image_large = image.resize(large_size, Image.Resampling.LANCZOS)

        # Rotate with high-quality resampling
        rotated_large = image_large.rotate(angle, expand=True,
                                          fillcolor=(255, 255, 255),
                                          resample=Image.Resampling.BICUBIC)

        # Calculate new size maintaining aspect ratio
        scale = min(original_size[0] * upscale_factor / rotated_large.width,
                   original_size[1] * upscale_factor / rotated_large.height)
        new_size = (int(rotated_large.width * scale),
                   int(rotated_large.height * scale))

        # Downscale back with high-quality resampling
        return rotated_large.resize(new_size, Image.Resampling.LANCZOS)

    def _apply_perspective(self, img_array: np.ndarray) -> np.ndarray:
        h, w = img_array.shape[:2]

        # Define source points (corners of the original image)
        pts1 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])

        # Add random distortion to destination points
        distortion = self.perspective_distortion * min(w, h)
        pts2 = pts1.copy()

        for i in range(4):
            pts2[i][0] += random.uniform(-distortion, distortion)
            pts2[i][1] += random.uniform(-distortion, distortion)

        # Calculate perspective transform matrix
        matrix = cv2.getPerspectiveTransform(pts1, pts2)

        # Apply the perspective transformation with cubic interpolation for smoother results
        result = cv2.warpPerspective(img_array, matrix, (w, h),
                                    flags=cv2.INTER_CUBIC,
                                    borderMode=cv2.BORDER_CONSTANT,
                                    borderValue=(255, 255, 255))

        return result

    def _add_noise(self, img_array: np.ndarray) -> np.ndarray:
        noise_amount = random.uniform(*self.noise_level)
        if noise_amount == 0:
            return img_array

        # Add Gaussian noise
        noise = np.random.normal(0, noise_amount * 255, img_array.shape)
        noisy_image = img_array + noise

        # Clip values to valid range
        noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)

        return noisy_image

    def _apply_blur(self, image: Image.Image) -> Image.Image:
        blur_radius = random.uniform(*self.blur_range)
        if blur_radius > 0:
            return image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        return image

    def _adjust_brightness(self, image: Image.Image) -> Image.Image:
        factor = random.uniform(*self.brightness_range)
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

    def _adjust_contrast(self, image: Image.Image) -> Image.Image:
        factor = random.uniform(*self.contrast_range)
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    def _add_crumple_effect(self, img_array: np.ndarray) -> np.ndarray:
        h, w = img_array.shape[:2]

        # Create displacement maps for x and y
        displacement_x = np.zeros((h, w), dtype=np.float32)
        displacement_y = np.zeros((h, w), dtype=np.float32)

        # Add multiple sine waves for crumple effect
        for _ in range(3):
            freq_x = random.uniform(0.01, 0.05)
            freq_y = random.uniform(0.01, 0.05)
            amplitude = random.uniform(1, 5) * self.crumple_intensity

            for i in range(h):
                for j in range(w):
                    displacement_x[i, j] += amplitude * np.sin(2 * np.pi * freq_x * j)
                    displacement_y[i, j] += amplitude * np.sin(2 * np.pi * freq_y * i)

        # Create meshgrid and apply displacement
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        x_displaced = (x + displacement_x).astype(np.float32)
        y_displaced = (y + displacement_y).astype(np.float32)

        # Remap the image
        result = cv2.remap(img_array, x_displaced, y_displaced,
                          cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        return result

    def _add_shadow(self, image: Image.Image) -> Image.Image:
        # Create a gradient shadow overlay
        img_array = np.array(image)
        h, w = img_array.shape[:2]

        # Create shadow gradient
        shadow = np.zeros((h, w), dtype=np.uint8)

        # Random shadow parameters
        shadow_intensity = random.uniform(0.1, 0.3)
        shadow_angle = random.uniform(0, 360)

        # Create gradient based on angle
        center_x = w * random.uniform(0.3, 0.7)
        center_y = h * random.uniform(0.3, 0.7)

        for i in range(h):
            for j in range(w):
                dist = np.sqrt((i - center_y)**2 + (j - center_x)**2)
                shadow[i, j] = max(0, 255 - int(dist * 0.5))

        # Apply Gaussian blur to soften shadow
        shadow = cv2.GaussianBlur(shadow, (21, 21), 0)

        # Blend shadow with image
        for c in range(3):
            img_array[:, :, c] = (img_array[:, :, c] * (1 - shadow_intensity * shadow / 255)).astype(np.uint8)

        return Image.fromarray(img_array)


class RealisticEffects:
    @staticmethod
    def add_fold_lines(image: Image.Image, num_folds: int = 2) -> Image.Image:
        img_array = np.array(image)
        h, w = img_array.shape[:2]

        for _ in range(num_folds):
            # Random fold position and angle
            if random.random() > 0.5:
                # Horizontal fold
                y = random.randint(int(h * 0.2), int(h * 0.8))
                cv2.line(img_array, (0, y), (w, y), (200, 200, 200), 1)

                # Add slight darkening along fold
                for offset in range(-2, 3):
                    if 0 <= y + offset < h:
                        img_array[y + offset, :] = (img_array[y + offset, :] * 0.95).astype(np.uint8)
            else:
                # Vertical fold
                x = random.randint(int(w * 0.2), int(w * 0.8))
                cv2.line(img_array, (x, 0), (x, h), (200, 200, 200), 1)

                # Add slight darkening along fold
                for offset in range(-2, 3):
                    if 0 <= x + offset < w:
                        img_array[:, x + offset] = (img_array[:, x + offset] * 0.95).astype(np.uint8)

        return Image.fromarray(img_array)

    @staticmethod
    def add_coffee_stain(image: Image.Image) -> Image.Image:
        img_array = np.array(image)
        h, w = img_array.shape[:2]

        # Random stain position
        cx = random.randint(int(w * 0.1), int(w * 0.9))
        cy = random.randint(int(h * 0.1), int(h * 0.9))

        # Random stain size
        radius = random.randint(20, 60)

        # Create stain mask
        mask = np.zeros((h, w), dtype=np.float32)
        cv2.circle(mask, (cx, cy), radius, 1.0, -1)

        # Add some irregularity
        mask = cv2.GaussianBlur(mask, (21, 21), 0)

        # Brown color for coffee
        stain_color = np.array([139, 90, 43])  # Brown in BGR

        # Apply stain
        for c in range(3):
            img_array[:, :, c] = (img_array[:, :, c] * (1 - mask * 0.3) +
                                 stain_color[c] * mask * 0.3).astype(np.uint8)

        return Image.fromarray(img_array)