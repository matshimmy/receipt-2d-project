from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple, Optional
import os
from pathlib import Path
from .templates import ReceiptTemplate, ElementType, Alignment


class ReceiptRenderer:
    def __init__(self, font_dir: Optional[str] = None):
        self.font_dir = font_dir or Path(__file__).parent / "fonts"
        self.default_fonts = {
            "regular": self._load_font("DejaVuSans.ttf", 12),
            "bold": self._load_font("DejaVuSans-Bold.ttf", 12)
        }

    def _load_font(self, font_name: str, size: int):
        try:
            if self.font_dir and os.path.exists(self.font_dir / font_name):
                return ImageFont.truetype(str(self.font_dir / font_name), size)
        except:
            pass

        # Fallback to default font
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()

    def _get_font(self, size: int, bold: bool = False):
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
        # Create blank receipt
        image = Image.new('RGB', (template.width, template.height), template.background_color)
        draw = ImageDraw.Draw(image)

        # Process each element
        for element in template.elements:
            if element.type == ElementType.TEXT:
                self._draw_text(draw, element, template)
            elif element.type == ElementType.LINE:
                self._draw_line(draw, element, template)

        if output_path:
            image.save(output_path)

        return image

    def _draw_text(self, draw: ImageDraw.Draw, element, template: ReceiptTemplate):
        font = self._get_font(element.font_size, element.bold)

        # Get text bbox for alignment
        bbox = draw.textbbox((0, 0), element.content, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x, y = element.position

        # Adjust x based on alignment
        if element.alignment == Alignment.CENTER:
            x = x - text_width // 2
        elif element.alignment == Alignment.RIGHT:
            x = x - text_width

        # Draw text
        draw.text((x, y), element.content, fill=template.text_color, font=font)

    def _draw_line(self, draw: ImageDraw.Draw, element, template: ReceiptTemplate):
        x, y = element.position
        width = element.width or (template.width - 2 * template.padding)

        # Draw horizontal line
        draw.line([(x, y), (x + width, y)], fill=template.text_color, width=1)


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

        template.add_footer(
            transaction_id=transaction["transaction_id"],
            date_time=transaction["timestamp"],
            start_y=y + 10
        )

        # Render the receipt
        return self.renderer.render(template)