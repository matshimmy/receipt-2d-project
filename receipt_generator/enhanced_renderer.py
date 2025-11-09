"""
Enhanced renderer that tracks actual text positions for accurate bounding boxes.
"""

from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple, Optional
import os
from pathlib import Path
from .templates import ReceiptTemplate, ElementType, Alignment
from .renderer import ReceiptRenderer


class EnhancedReceiptRenderer(ReceiptRenderer):
    """Renderer that tracks actual text positions for bounding box generation."""

    def __init__(self, font_dir: Optional[str] = None, use_font_variations: bool = True):
        super().__init__(font_dir, use_font_variations)
        self.text_regions = []  # Store text regions with their bounding boxes

    def render_with_positions(self, template: ReceiptTemplate, output_path: Optional[str] = None) -> Tuple[Image.Image, List[Dict]]:
        """
        Render receipt and return image with text position data.

        Returns:
            Tuple of (image, text_regions) where text_regions contains bbox data
        """
        # Clear previous text regions
        self.text_regions = []

        # Render at 2x resolution for better quality (supersampling)
        scale_factor = 2
        high_res_width = template.width * scale_factor
        high_res_height = template.height * scale_factor

        # Create blank receipt at higher resolution
        image = Image.new('RGB', (high_res_width, high_res_height), template.background_color)
        draw = ImageDraw.Draw(image)

        # Process each element and track positions
        for element in template.elements:
            if element.type == ElementType.TEXT:
                self._draw_text_with_tracking(draw, element, template, scale_factor)
            elif element.type == ElementType.LINE:
                self._draw_line_scaled(draw, element, template, scale_factor)

        # Downscale with high-quality resampling for anti-aliasing
        image = image.resize((template.width, template.height), Image.Resampling.LANCZOS)

        # Adjust text regions for downscaling
        scaled_regions = []
        for region in self.text_regions:
            scaled_region = {
                "text": region["text"],
                "bbox": [
                    [point[0] / scale_factor, point[1] / scale_factor]
                    for point in region["bbox"]
                ],
                "type": region.get("type", "text")
            }
            scaled_regions.append(scaled_region)

        if output_path:
            image.save(output_path)

        return image, scaled_regions

    def _draw_text_with_tracking(self, draw: ImageDraw.Draw, element, template: ReceiptTemplate, scale: int):
        """Draw text and track its position."""
        # Scale font size
        font = self._get_font(element.font_size * scale, element.bold, element.type.value)

        # Process text content
        text_content = str(element.content)
        # Check if it's a currency value by looking at the content
        if text_content and text_content.replace('.', '', 1).replace('-', '', 1).isdigit():
            try:
                # Try to format as currency if it's a number
                val = float(text_content)
                if val > 0 and element.type == ElementType.TEXT:
                    # Only format as currency for positive numbers in text elements
                    # that look like prices (but let the template decide)
                    pass
            except:
                pass

        # Calculate text dimensions
        bbox = draw.textbbox((0, 0), text_content, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Scale position
        x, y = element.position[0] * scale, element.position[1] * scale

        # Apply alignment
        margin = template.padding * scale

        if element.alignment == Alignment.CENTER:
            x = (template.width * scale - text_width) // 2
        elif element.alignment == Alignment.RIGHT:
            x = template.width * scale - margin - text_width
        elif x < margin:
            x = margin
        elif x + text_width > (template.width * scale - margin):
            x = template.width * scale - margin - text_width

        # Draw text
        draw.text((x, y), text_content, fill=template.text_color, font=font)

        # Track the text region with 4 corner points
        # Format: [[x1,y1], [x2,y1], [x2,y2], [x1,y2]] (clockwise from top-left)
        text_region = {
            "text": text_content,
            "bbox": [
                [x, y],                           # top-left
                [x + text_width, y],              # top-right
                [x + text_width, y + text_height], # bottom-right
                [x, y + text_height]              # bottom-left
            ],
            "type": element.type.value
        }
        self.text_regions.append(text_region)


class EnhancedReceiptBuilder:
    """Builder that uses enhanced renderer for position tracking."""

    def __init__(self):
        self.renderer = EnhancedReceiptRenderer()
        self.transaction_data = None

    def build_from_transaction_with_positions(self, template: ReceiptTemplate, transaction: Dict) -> Tuple[Image.Image, List[Dict]]:
        """
        Build receipt and return image with accurate text positions.

        Returns:
            Tuple of (image, text_regions) where text_regions contains actual bounding boxes
        """
        # Store transaction data for reference
        self.transaction_data = transaction

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

        # Render with position tracking
        return self.renderer.render_with_positions(template)