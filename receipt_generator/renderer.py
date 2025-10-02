from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple, Optional
import os
import random
from pathlib import Path
from .templates import ReceiptTemplate, ElementType, Alignment
from .fonts import FontManager, FontCategory, TextVariations


class ReceiptRenderer:
    def __init__(self, font_dir: Optional[str] = None, use_font_variations: bool = True):
        self.font_dir = font_dir or Path(__file__).parent / "fonts"
        self.use_font_variations = use_font_variations
        self.font_manager = FontManager() if use_font_variations else None
        self.text_variations = TextVariations() if use_font_variations else None

        # Select a random font configuration for this receipt
        if self.use_font_variations:
            styles = ["thermal_classic", "modern_pos", "boutique", "retro"]
            self.font_config = self.font_manager.get_receipt_config(random.choice(styles))
            self.text_config = TextVariations.get_random_variations()
        else:
            self.font_config = None
            self.text_config = None

    def _get_font(self, size: int, bold: bool = False, element_type: str = "items"):
        # Use font manager if available
        if self.use_font_variations and self.font_manager and self.font_config:
            # Get configuration for this element type
            element_configs = {
                "store_name": "header",
                "address": "header",
                "phone": "footer",
                "item_name": "items",
                "item_price": "items",
                "quantity": "items",
                "subtotal": "totals",
                "tax": "totals",
                "total": "totals",
                "transaction": "footer",
                "timestamp": "footer",
                "thank_you": "footer"
            }

            config_key = element_configs.get(element_type, "items")
            config = self.font_config.get(config_key, {})

            # Apply size multiplier
            adjusted_size = int(size * config.get("size_multiplier", 1.0))

            # Get font from manager
            category = config.get("family", FontCategory.RECEIPT)
            use_bold = config.get("bold", bold)

            return self.font_manager.get_font(category, adjusted_size, bold=use_bold)

        # Fallback to original method
        try:
            if bold:
                font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
            else:
                font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
        except:
            pass

        # Try DejaVu fonts
        try:
            if bold:
                return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
            else:
                return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except:
            return ImageFont.load_default()

    def render(self, template: ReceiptTemplate, output_path: Optional[str] = None) -> Image.Image:
        # Render at 2x resolution for better quality (supersampling)
        scale_factor = 2
        high_res_width = template.width * scale_factor
        high_res_height = template.height * scale_factor

        # Create blank receipt at higher resolution
        image = Image.new('RGB', (high_res_width, high_res_height), template.background_color)
        draw = ImageDraw.Draw(image)

        # Process each element with scaled positions and sizes
        for element in template.elements:
            if element.type == ElementType.TEXT:
                self._draw_text_scaled(draw, element, template, scale_factor)
            elif element.type == ElementType.LINE:
                self._draw_line_scaled(draw, element, template, scale_factor)

        # Downscale with high-quality resampling for anti-aliasing
        image = image.resize((template.width, template.height), Image.Resampling.LANCZOS)

        if output_path:
            image.save(output_path)

        return image

    def _draw_text_scaled(self, draw: ImageDraw.Draw, element, template: ReceiptTemplate, scale: int):
        # Get element type for font selection
        elem_type = getattr(element, 'element_type', 'text')

        # Apply text transformations if configured
        text_content = element.content
        if self.text_variations and elem_type in ["store_name", "total", "subtotal"]:
            if self.text_variations.should_use_all_caps(elem_type):
                text_content = text_content.upper()

        # Scale up font size and get appropriate font
        font = self._get_font(element.font_size * scale, element.bold, elem_type)

        # Scale up position
        x, y = element.position[0] * scale, element.position[1] * scale

        # Apply character spacing if configured
        if self.text_config and self.text_config.get("char_spacing"):
            spacing_mult = TextVariations.get_character_spacing(self.text_config["char_spacing"])
            # For character spacing, we might need to draw each character separately
            # For now, we'll use the normal method
            pass

        # Get text bbox for alignment
        bbox = draw.textbbox((0, 0), text_content, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Check if text would overflow horizontally and truncate if needed
        max_width = (template.width - 2 * template.padding) * scale
        if text_width > max_width:
            # Truncate text to fit
            while text_width > max_width and len(text_content) > 3:
                text_content = text_content[:-1]
                bbox = draw.textbbox((0, 0), text_content + "...", font=font)
                text_width = bbox[2] - bbox[0]
            text_content = text_content + "..."

        # Adjust x based on alignment
        if element.alignment == Alignment.CENTER:
            x = x - text_width // 2
        elif element.alignment == Alignment.RIGHT:
            x = x - text_width

        # Ensure text doesn't go off the page
        margin = template.padding * scale // 2
        if x < margin:
            x = margin
        elif x + text_width > (template.width * scale - margin):
            x = template.width * scale - margin - text_width

        # Draw text
        draw.text((x, y), text_content, fill=template.text_color, font=font)

    def _draw_line_scaled(self, draw: ImageDraw.Draw, element, template: ReceiptTemplate, scale: int):
        # Scale up position and width
        x, y = element.position[0] * scale, element.position[1] * scale
        width = (element.width or (template.width - 2 * template.padding)) * scale

        # Draw horizontal line with scaled width for smoother appearance
        draw.line([(x, y), (x + width, y)], fill=template.text_color, width=scale)



class ReceiptBuilder:
    def __init__(self):
        self.renderer = ReceiptRenderer()

    def build_from_transaction(self, template: ReceiptTemplate, transaction: Dict) -> Image.Image:
        # Clear existing elements
        template.elements = []

        # Build receipt structure
        y = template.add_header(
            store_name=transaction["store"]["name"],
            address=transaction["store"]["address"],
            phone=transaction["store"]["phone"]
        )

        y = template.add_items(transaction["items"], y + 10)

        y = template.add_totals(
            subtotal=transaction["subtotal"],
            tax=transaction["tax"],
            total=transaction["total"],
            start_y=y + 10
        )

        y = template.add_footer(
            transaction_id=transaction["transaction_id"],
            date_time=transaction["timestamp"],
            start_y=y + 10
        )

        # Add promotional text at the bottom (30% chance)
        template.add_promotional_text(start_y=y)

        # Render the receipt
        return self.renderer.render(template)