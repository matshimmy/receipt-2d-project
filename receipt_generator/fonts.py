import os
import random
from typing import Dict, List, Optional, Tuple
from PIL import ImageFont
from pathlib import Path
from enum import Enum


class FontStyle(Enum):
    REGULAR = "regular"
    BOLD = "bold"
    ITALIC = "italic"
    BOLD_ITALIC = "bold_italic"
    CONDENSED = "condensed"
    LIGHT = "light"
    MONOSPACE = "monospace"


class FontCategory(Enum):
    THERMAL = "thermal"        # Monospace fonts for thermal printers
    MODERN = "modern"          # Clean sans-serif fonts
    CLASSIC = "classic"        # Traditional serif fonts
    RECEIPT = "receipt"        # Typical receipt fonts
    DOT_MATRIX = "dot_matrix"  # Pixelated/bitmap style


class FontManager:
    def __init__(self):
        self.font_paths = self._discover_system_fonts()
        self.font_families = self._organize_font_families()
        self.receipt_fonts = self._setup_receipt_fonts()
        self._fallback_font = None

    def _discover_system_fonts(self) -> Dict[str, List[str]]:
        """Discover available system fonts"""
        font_dirs = [
            "/usr/share/fonts/truetype",
            "/usr/local/share/fonts",
            "/System/Library/Fonts",  # macOS
            "C:\\Windows\\Fonts",      # Windows
            os.path.expanduser("~/.fonts"),
            os.path.expanduser("~/.local/share/fonts")
        ]

        fonts = {
            "liberation": [],
            "dejavu": [],
            "courier": [],
            "arial": [],
            "helvetica": [],
            "times": [],
            "ubuntu": [],
            "roboto": [],
            "noto": []
        }

        for font_dir in font_dirs:
            if not os.path.exists(font_dir):
                continue

            for root, dirs, files in os.walk(font_dir):
                for file in files:
                    if file.lower().endswith(('.ttf', '.otf')):
                        font_path = os.path.join(root, file)
                        file_lower = file.lower()

                        # Categorize fonts
                        for family in fonts.keys():
                            if family in file_lower:
                                fonts[family].append(font_path)

        return fonts

    def _organize_font_families(self) -> Dict[FontCategory, Dict[str, List[str]]]:
        """Organize fonts by category and style"""
        families = {
            FontCategory.THERMAL: {
                "primary": self._find_monospace_fonts(),
                "alternatives": []
            },
            FontCategory.MODERN: {
                "primary": self._find_sans_serif_fonts(),
                "alternatives": []
            },
            FontCategory.CLASSIC: {
                "primary": self._find_serif_fonts(),
                "alternatives": []
            },
            FontCategory.RECEIPT: {
                "primary": self._find_receipt_fonts(),
                "alternatives": []
            },
            FontCategory.DOT_MATRIX: {
                "primary": self._find_monospace_fonts(),
                "alternatives": []
            }
        }
        return families

    def _find_monospace_fonts(self) -> List[str]:
        """Find monospace fonts for thermal/dot matrix styles"""
        monospace = []

        # Look for courier fonts
        monospace.extend(self.font_paths.get("courier", []))

        # Look for common monospace fonts
        patterns = ["mono", "courier", "consolas", "fixed", "terminal"]
        for family, paths in self.font_paths.items():
            for path in paths:
                basename = os.path.basename(path).lower()
                if any(p in basename for p in patterns):
                    monospace.append(path)

        # Fallback paths
        fallback_paths = [
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf"
        ]

        for path in fallback_paths:
            if os.path.exists(path) and path not in monospace:
                monospace.append(path)

        return monospace

    def _find_sans_serif_fonts(self) -> List[str]:
        """Find sans-serif fonts for modern receipts"""
        sans_serif = []

        # Primary choices
        sans_serif.extend(self.font_paths.get("liberation", []))
        sans_serif.extend(self.font_paths.get("arial", []))
        sans_serif.extend(self.font_paths.get("helvetica", []))
        sans_serif.extend(self.font_paths.get("roboto", []))

        # Fallback paths
        fallback_paths = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]

        for path in fallback_paths:
            if os.path.exists(path) and path not in sans_serif:
                sans_serif.append(path)

        return sans_serif

    def _find_serif_fonts(self) -> List[str]:
        """Find serif fonts for classic receipts"""
        serif = []

        serif.extend(self.font_paths.get("times", []))

        # Look for serif fonts
        patterns = ["serif", "times", "georgia", "book"]
        for family, paths in self.font_paths.items():
            for path in paths:
                basename = os.path.basename(path).lower()
                if any(p in basename for p in patterns) and "sans" not in basename:
                    serif.append(path)

        # Fallback
        fallback_paths = [
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
        ]

        for path in fallback_paths:
            if os.path.exists(path) and path not in serif:
                serif.append(path)

        return serif

    def _find_receipt_fonts(self) -> List[str]:
        """Find typical receipt fonts"""
        receipt = []

        # Mix of mono and sans-serif that look good on receipts
        receipt.extend(self._find_monospace_fonts()[:2])
        receipt.extend(self._find_sans_serif_fonts()[:2])

        return receipt

    def _setup_receipt_fonts(self) -> Dict[str, Dict]:
        """Setup specific receipt font configurations"""
        configs = {
            "thermal_classic": {
                "header": {"family": FontCategory.THERMAL, "size_multiplier": 1.2, "bold": True},
                "items": {"family": FontCategory.THERMAL, "size_multiplier": 1.0, "bold": False},
                "totals": {"family": FontCategory.THERMAL, "size_multiplier": 1.1, "bold": True},
                "footer": {"family": FontCategory.THERMAL, "size_multiplier": 0.8, "bold": False}
            },
            "modern_pos": {
                "header": {"family": FontCategory.MODERN, "size_multiplier": 1.3, "bold": True},
                "items": {"family": FontCategory.MODERN, "size_multiplier": 1.0, "bold": False},
                "totals": {"family": FontCategory.MODERN, "size_multiplier": 1.15, "bold": True},
                "footer": {"family": FontCategory.MODERN, "size_multiplier": 0.9, "bold": False}
            },
            "boutique": {
                "header": {"family": FontCategory.CLASSIC, "size_multiplier": 1.4, "bold": False},
                "items": {"family": FontCategory.RECEIPT, "size_multiplier": 1.0, "bold": False},
                "totals": {"family": FontCategory.MODERN, "size_multiplier": 1.1, "bold": True},
                "footer": {"family": FontCategory.CLASSIC, "size_multiplier": 0.85, "bold": False}
            },
            "retro": {
                "header": {"family": FontCategory.DOT_MATRIX, "size_multiplier": 1.2, "bold": True},
                "items": {"family": FontCategory.DOT_MATRIX, "size_multiplier": 1.0, "bold": False},
                "totals": {"family": FontCategory.DOT_MATRIX, "size_multiplier": 1.1, "bold": True},
                "footer": {"family": FontCategory.DOT_MATRIX, "size_multiplier": 0.9, "bold": False}
            }
        }
        return configs

    def get_font(self, category: FontCategory, size: int, bold: bool = False,
                 italic: bool = False) -> ImageFont.FreeTypeFont:
        """Get a font with specified parameters"""
        fonts = self.font_families.get(category, {}).get("primary", [])

        if not fonts:
            return self._get_fallback_font(size)

        # Try to find matching style
        selected = None
        for font_path in fonts:
            basename = os.path.basename(font_path).lower()

            # Check for style match
            if bold and italic and ("bolditalic" in basename or "bi" in basename):
                selected = font_path
                break
            elif bold and "bold" in basename and "italic" not in basename:
                selected = font_path
                break
            elif italic and "italic" in basename and "bold" not in basename:
                selected = font_path
                break
            elif not bold and not italic and "regular" in basename:
                selected = font_path
                break

        # Fallback to first available
        if not selected:
            selected = fonts[0]

        try:
            return ImageFont.truetype(selected, size)
        except:
            return self._get_fallback_font(size)

    def get_random_font(self, size: int, style_preference: Optional[FontStyle] = None) -> ImageFont.FreeTypeFont:
        """Get a random font for variety"""
        all_fonts = []
        for family_fonts in self.font_paths.values():
            all_fonts.extend(family_fonts)

        if not all_fonts:
            return self._get_fallback_font(size)

        if style_preference:
            # Filter by style
            filtered = []
            style_keywords = {
                FontStyle.BOLD: ["bold"],
                FontStyle.ITALIC: ["italic", "oblique"],
                FontStyle.LIGHT: ["light", "thin"],
                FontStyle.CONDENSED: ["condensed", "narrow"],
                FontStyle.MONOSPACE: ["mono", "fixed"]
            }

            keywords = style_keywords.get(style_preference, [])
            for font in all_fonts:
                basename = os.path.basename(font).lower()
                if any(kw in basename for kw in keywords):
                    filtered.append(font)

            if filtered:
                all_fonts = filtered

        selected = random.choice(all_fonts)
        try:
            return ImageFont.truetype(selected, size)
        except:
            return self._get_fallback_font(size)

    def get_receipt_config(self, style: str = "thermal_classic") -> Dict:
        """Get a complete font configuration for a receipt style"""
        return self.receipt_fonts.get(style, self.receipt_fonts["thermal_classic"])

    def _get_fallback_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get fallback font when nothing else works"""
        if not self._fallback_font:
            fallbacks = [
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "arial.ttf"
            ]

            for path in fallbacks:
                try:
                    self._fallback_font = path
                    return ImageFont.truetype(path, size)
                except:
                    continue

        if self._fallback_font:
            try:
                return ImageFont.truetype(self._fallback_font, size)
            except:
                pass

        # Ultimate fallback
        return ImageFont.load_default()


class TextVariations:
    """Apply various text rendering variations"""

    @staticmethod
    def get_character_spacing(style: str = "normal") -> float:
        """Get character spacing multiplier"""
        spacings = {
            "condensed": 0.85,
            "normal": 1.0,
            "expanded": 1.15,
            "wide": 1.3
        }
        return spacings.get(style, 1.0)

    @staticmethod
    def get_line_spacing(style: str = "normal") -> float:
        """Get line spacing multiplier"""
        spacings = {
            "tight": 0.9,
            "normal": 1.0,
            "loose": 1.2,
            "double": 1.5
        }
        return spacings.get(style, 1.0)

    @staticmethod
    def should_use_all_caps(element_type: str) -> bool:
        """Determine if element should be in all caps"""
        # Common receipt elements that are often in caps
        caps_elements = ["store_name", "total", "subtotal", "tax", "transaction_id"]
        return element_type in caps_elements and random.random() < 0.6

    @staticmethod
    def apply_text_transform(text: str, transform: str = "none") -> str:
        """Apply text transformations"""
        if transform == "uppercase":
            return text.upper()
        elif transform == "lowercase":
            return text.lower()
        elif transform == "title":
            return text.title()
        elif transform == "small_caps":
            # Simulate small caps by mixing upper and lower
            return ''.join(c.upper() if i % 2 == 0 else c.lower()
                          for i, c in enumerate(text))
        return text

    @staticmethod
    def get_random_variations() -> Dict:
        """Get random text variations for natural variety"""
        return {
            "char_spacing": random.choice(["condensed", "normal", "expanded"]),
            "line_spacing": random.choice(["tight", "normal", "loose"]),
            "header_transform": random.choice(["uppercase", "title", "none"]),
            "use_bold_items": random.random() < 0.3,
            "use_italic_price": random.random() < 0.2
        }