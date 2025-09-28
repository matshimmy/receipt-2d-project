from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
from enum import Enum
import random as rand
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np


class ReceiptStyle(Enum):
    THERMAL = "thermal"
    INKJET = "inkjet"
    DOT_MATRIX = "dot_matrix"
    MODERN_POS = "modern_pos"
    CARBON_COPY = "carbon_copy"


class PaperQuality(Enum):
    CRISP = "crisp"
    AGED = "aged"
    CHEAP = "cheap"
    GLOSSY = "glossy"


@dataclass
class StyleSettings:
    background_color: Tuple[int, int, int]
    text_color: Tuple[int, int, int]
    font_style: str
    char_spacing: float
    line_spacing: float
    print_quality: float  # 0.5 = low quality, 1.0 = perfect
    ink_variation: float  # How much ink varies (fading effect)
    paper_texture: Optional[str] = None


class ReceiptStyleManager:
    def __init__(self):
        self.styles = {
            ReceiptStyle.THERMAL: StyleSettings(
                background_color=(248, 248, 248),  # Slight off-white
                text_color=(40, 40, 40),  # Dark gray (thermal doesn't print pure black)
                font_style="monospace",
                char_spacing=1.0,
                line_spacing=1.1,
                print_quality=0.85,
                ink_variation=0.15,
                paper_texture="smooth"
            ),
            ReceiptStyle.INKJET: StyleSettings(
                background_color=(255, 255, 255),
                text_color=(0, 0, 0),
                font_style="sans-serif",
                char_spacing=1.0,
                line_spacing=1.2,
                print_quality=0.95,
                ink_variation=0.05,
                paper_texture="standard"
            ),
            ReceiptStyle.DOT_MATRIX: StyleSettings(
                background_color=(252, 252, 250),
                text_color=(20, 20, 80),  # Slight blue tint
                font_style="monospace",
                char_spacing=1.2,
                line_spacing=1.3,
                print_quality=0.7,
                ink_variation=0.2,
                paper_texture="perforated"
            ),
            ReceiptStyle.MODERN_POS: StyleSettings(
                background_color=(255, 255, 255),
                text_color=(0, 0, 0),
                font_style="modern",
                char_spacing=0.95,
                line_spacing=1.15,
                print_quality=1.0,
                ink_variation=0.0,
                paper_texture="glossy"
            ),
            ReceiptStyle.CARBON_COPY: StyleSettings(
                background_color=(250, 248, 245),
                text_color=(60, 60, 100),  # Blue-ish carbon copy look
                font_style="typewriter",
                char_spacing=1.1,
                line_spacing=1.25,
                print_quality=0.75,
                ink_variation=0.25,
                paper_texture="thin"
            )
        }

    def get_style(self, style: ReceiptStyle) -> StyleSettings:
        return self.styles.get(style, self.styles[ReceiptStyle.THERMAL])

    def apply_style_effects(self, image: Image.Image, style: ReceiptStyle) -> Image.Image:
        settings = self.get_style(style)

        if style == ReceiptStyle.THERMAL:
            image = self._apply_thermal_effects(image, settings)
        elif style == ReceiptStyle.DOT_MATRIX:
            image = self._apply_dot_matrix_effects(image, settings)
        elif style == ReceiptStyle.CARBON_COPY:
            image = self._apply_carbon_copy_effects(image, settings)

        # Apply print quality
        if settings.print_quality < 1.0:
            image = self._degrade_print_quality(image, settings.print_quality)

        return image

    def _apply_thermal_effects(self, image: Image.Image, settings: StyleSettings) -> Image.Image:
        # Add slight horizontal banding (thermal print head lines)
        img_array = np.array(image)
        h, w = img_array.shape[:2]

        for y in range(0, h, 3):
            if rand.random() < 0.1:  # 10% chance of slight line
                img_array[y:y+1, :] = np.clip(img_array[y:y+1, :] * 0.95, 0, 255)

        # Simulate thermal fading on edges
        fade_width = 20
        for x in range(fade_width):
            factor = 0.9 + (0.1 * x / fade_width)
            img_array[:, x] = np.clip(img_array[:, x] * factor, 0, 255)
            img_array[:, -(x+1)] = np.clip(img_array[:, -(x+1)] * factor, 0, 255)

        return Image.fromarray(img_array.astype(np.uint8))

    def _apply_dot_matrix_effects(self, image: Image.Image, settings: StyleSettings) -> Image.Image:
        # Create dot pattern overlay
        img_array = np.array(image)
        h, w = img_array.shape[:2]

        # Create dots pattern
        dot_size = 2
        dot_spacing = 3

        for y in range(0, h, dot_spacing):
            for x in range(0, w, dot_spacing):
                if img_array[y, x].mean() < 200:  # Only on darker areas
                    # Make a small dot pattern
                    y1, y2 = max(0, y-1), min(h, y+dot_size)
                    x1, x2 = max(0, x-1), min(w, x+dot_size)
                    img_array[y1:y2, x1:x2] = np.clip(
                        img_array[y1:y2, x1:x2] * 0.8, 0, 255
                    )

        return Image.fromarray(img_array.astype(np.uint8))

    def _apply_carbon_copy_effects(self, image: Image.Image, settings: StyleSettings) -> Image.Image:
        # Add pressure variations
        img_array = np.array(image)

        # Random pressure zones
        h, w = img_array.shape[:2]
        for _ in range(5):
            cx = rand.randint(0, w)
            cy = rand.randint(0, h)
            radius = rand.randint(30, 100)

            for y in range(max(0, cy-radius), min(h, cy+radius)):
                for x in range(max(0, cx-radius), min(w, cx+radius)):
                    dist = np.sqrt((x-cx)**2 + (y-cy)**2)
                    if dist < radius:
                        factor = 0.8 + 0.2 * (dist / radius)
                        img_array[y, x] = np.clip(img_array[y, x] * factor, 0, 255)

        # Add slight double-strike effect
        shifted = np.roll(img_array, 1, axis=1)
        img_array = (img_array * 0.7 + shifted * 0.3).astype(np.uint8)

        return Image.fromarray(img_array)

    def _degrade_print_quality(self, image: Image.Image, quality: float) -> Image.Image:
        if quality >= 1.0:
            return image

        # Add noise based on quality
        img_array = np.array(image)
        noise_amount = (1.0 - quality) * 20
        noise = np.random.normal(0, noise_amount, img_array.shape)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)

        return Image.fromarray(img_array)


class LogoGenerator:
    def __init__(self):
        self.shapes = ["circle", "square", "rounded_rect", "diamond", "triangle"]
        self.styles = ["minimal", "bold", "outline", "gradient"]

    def generate_logo(self, store_name: str, size: Tuple[int, int] = (80, 40)) -> Image.Image:
        logo = Image.new('RGBA', size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(logo)

        # Use store name to seed rand choices for consistency
        seed = sum(ord(c) for c in store_name)
        rand.seed(seed)

        shape = rand.choice(self.shapes)
        style = rand.choice(self.styles)
        color = self._generate_brand_color(seed)

        # Draw background shape
        if shape == "circle":
            draw.ellipse([5, 5, size[0]-5, size[1]-5], fill=color, outline=color)
        elif shape == "square":
            draw.rectangle([5, 5, size[0]-5, size[1]-5], fill=color, outline=color)
        elif shape == "rounded_rect":
            self._draw_rounded_rect(draw, [5, 5, size[0]-5, size[1]-5], 8, fill=color)
        elif shape == "diamond":
            points = [
                (size[0]//2, 5),
                (size[0]-5, size[1]//2),
                (size[0]//2, size[1]-5),
                (5, size[1]//2)
            ]
            draw.polygon(points, fill=color, outline=color)
        elif shape == "triangle":
            points = [(size[0]//2, 5), (size[0]-5, size[1]-5), (5, size[1]-5)]
            draw.polygon(points, fill=color, outline=color)

        # Add store initials
        initials = ''.join(word[0] for word in store_name.split()[:2]).upper()
        if len(initials) == 0:
            initials = store_name[:2].upper()

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                                    size[1]//3)
        except:
            font = ImageFont.load_default()

        # Draw text
        text_color = (255, 255, 255) if style in ["minimal", "bold"] else color
        if style == "outline":
            # Draw shape outline only
            logo = Image.new('RGBA', size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(logo)
            if shape == "circle":
                draw.ellipse([5, 5, size[0]-5, size[1]-5], outline=color, width=2)
            elif shape == "square":
                draw.rectangle([5, 5, size[0]-5, size[1]-5], outline=color, width=2)

        # Add text
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (size[0] - text_width) // 2
        text_y = (size[1] - text_height) // 2
        draw.text((text_x, text_y), initials, fill=text_color, font=font)

        rand.seed()  # Reset seed
        return logo

    def _generate_brand_color(self, seed: int) -> Tuple[int, int, int]:
        rand.seed(seed)
        hue = rand.randint(0, 360)

        # Convert HSV to RGB (simplified)
        c = 0.7  # Saturation
        x = c * (1 - abs((hue / 60) % 2 - 1))
        m = 0.3

        if hue < 60:
            r, g, b = c, x, 0
        elif hue < 120:
            r, g, b = x, c, 0
        elif hue < 180:
            r, g, b = 0, c, x
        elif hue < 240:
            r, g, b = 0, x, c
        elif hue < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)

        rand.seed()
        return (r, g, b)

    def _draw_rounded_rect(self, draw, bbox, radius, fill):
        x0, y0, x1, y1 = bbox
        draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
        draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
        draw.ellipse([x0, y0, x0 + 2*radius, y0 + 2*radius], fill=fill)
        draw.ellipse([x1 - 2*radius, y0, x1, y0 + 2*radius], fill=fill)
        draw.ellipse([x0, y1 - 2*radius, x0 + 2*radius, y1], fill=fill)
        draw.ellipse([x1 - 2*radius, y1 - 2*radius, x1, y1], fill=fill)


class ReceiptVariations:
    @staticmethod
    def get_random_width() -> int:
        # Common receipt widths
        widths = [280, 300, 320, 350, 380, 400]
        return rand.choice(widths)

    @staticmethod
    def get_random_font_size_multiplier() -> float:
        # Slight variations in font size
        return rand.uniform(0.9, 1.1)

    @staticmethod
    def get_random_margin() -> int:
        # Different margin sizes
        return rand.choice([15, 20, 25, 30])

    @staticmethod
    def should_include_barcode() -> bool:
        return rand.random() < 0.3  # 30% chance

    @staticmethod
    def should_include_qr_code() -> bool:
        return rand.random() < 0.15  # 15% chance

    @staticmethod
    def get_random_footer_text() -> List[str]:
        options = [
            ["Thank you for your business!"],
            ["Have a great day!"],
            ["Thank you! Please come again"],
            ["Customer Copy"],
            ["Keep this receipt for your records"],
            ["Thank you for shopping with us!"],
            ["Visit us online at www.example.com"],
            ["Questions? Call 1-800-EXAMPLE"],
            ["CUSTOMER SATISFACTION GUARANTEED"],
            ["Save this receipt for returns"]
        ]
        return rand.choice(options)