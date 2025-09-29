import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image
import uuid
from datetime import datetime
import random

from .templates import ReceiptTemplate, TemplateLibrary
from .data_generator import ProductDatabase
from .renderer import ReceiptBuilder
from .augmentation import AugmentationPipeline, RealisticEffects
from .styles import ReceiptStyleManager, ReceiptStyle, ReceiptVariations


class ReceiptGenerator:
    def __init__(self,
                 output_dir: str = "output",
                 enable_augmentation: bool = True,
                 seed: Optional[int] = None):

        self.output_dir = Path(output_dir)
        # Don't create directories in init - only when saving

        self.product_db = ProductDatabase(seed=seed)
        self.builder = ReceiptBuilder()
        self.augmentation = AugmentationPipeline() if enable_augmentation else None
        self.enable_augmentation = enable_augmentation
        self.style_manager = ReceiptStyleManager()

    def generate_single(self,
                       store_type: str = "grocery",
                       template: Optional[ReceiptTemplate] = None,
                       augmentations: Optional[List[str]] = None,
                       style: Optional[ReceiptStyle] = None) -> Tuple[Image.Image, Dict]:

        # Choose random style if not specified
        if style is None:
            style = random.choice(list(ReceiptStyle))

        # Apply style settings to template
        style_settings = self.style_manager.get_style(style)

        # Use template or create default with variations
        if template is None:
            # Add width variations
            width = ReceiptVariations.get_random_width()
            margin = ReceiptVariations.get_random_margin()

            if store_type == "grocery":
                template = TemplateLibrary.grocery_store()
            elif store_type == "restaurant":
                template = TemplateLibrary.restaurant()
            else:
                template = TemplateLibrary.retail_store()

            template.width = width
            template.padding = margin
            template.background_color = style_settings.background_color
            template.text_color = style_settings.text_color

        # Generate transaction data
        transaction = self.product_db.generate_transaction_data(store_type)

        # Build receipt image
        receipt_img = self.builder.build_from_transaction(template, transaction)

        # Apply style effects
        receipt_img = self.style_manager.apply_style_effects(receipt_img, style)

        # Generate metadata
        metadata = self._generate_metadata(template, transaction)

        # Apply augmentations if enabled
        if self.enable_augmentation and self.augmentation:
            if augmentations is None:
                augmentations = ["rotation", "noise", "blur", "brightness", "contrast"]

            receipt_img = self.augmentation.apply(receipt_img, augmentations)

            # Add realistic effects randomly
            if "realistic" in augmentations or (augmentations is None and self.enable_augmentation):
                if random.random() < 0.3:
                    receipt_img = RealisticEffects.add_fold_lines(receipt_img, num_folds=random.randint(1, 3))
                if random.random() < 0.1:
                    receipt_img = RealisticEffects.add_coffee_stain(receipt_img)

        return receipt_img, metadata

    def _generate_metadata(self, template: ReceiptTemplate, transaction: Dict) -> Dict:
        metadata = {
            "id": str(uuid.uuid4()),
            "generated_at": datetime.now().isoformat(),
            "template": template.name,
            "store": transaction["store"],
            "transaction_id": transaction["transaction_id"],
            "timestamp": transaction["timestamp"],
            "items": [],
            "totals": {
                "subtotal": transaction["subtotal"],
                "tax": transaction["tax"],
                "total": transaction["total"]
            },
            "text_regions": []
        }

        # Extract text regions with bounding boxes
        for element in template.elements:
            if hasattr(element, 'content') and element.content:
                region = {
                    "text": element.content,
                    "position": element.position,
                    "font_size": element.font_size,
                    "bold": element.bold,
                    "type": element.type.value
                }
                metadata["text_regions"].append(region)

        # Add item details
        for item in transaction["items"]:
            metadata["items"].append({
                "name": item["name"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
                "total": item["total"]
            })

        return metadata

    def generate_batch(self,
                      count: int = 100,
                      store_types: Optional[List[str]] = None,
                      save: bool = True) -> List[Tuple[Image.Image, Dict]]:

        if store_types is None:
            store_types = ["grocery", "restaurant", "retail"]

        results = []

        # Create directories only when saving
        if save:
            self.output_dir.mkdir(exist_ok=True, parents=True)
            (self.output_dir / "images").mkdir(exist_ok=True)
            (self.output_dir / "metadata").mkdir(exist_ok=True)

        for i in range(count):
            store_type = store_types[i % len(store_types)]

            # Generate receipt
            img, metadata = self.generate_single(store_type=store_type)

            if save:
                # Save image
                img_path = self.output_dir / "images" / f"{metadata['id']}.png"
                img.save(img_path)

                # Save metadata
                meta_path = self.output_dir / "metadata" / f"{metadata['id']}.json"
                with open(meta_path, 'w') as f:
                    json.dump(metadata, f, indent=2)

                # Update metadata with file path
                metadata["image_path"] = str(img_path)

            results.append((img, metadata))

            if (i + 1) % 10 == 0:
                print(f"Generated {i + 1}/{count} receipts")

        # Save summary
        if save:
            summary = {
                "total_generated": count,
                "timestamp": datetime.now().isoformat(),
                "store_types": store_types,
                "receipts": [meta["id"] for _, meta in results]
            }

            with open(self.output_dir / "generation_summary.json", 'w') as f:
                json.dump(summary, f, indent=2)

        return results