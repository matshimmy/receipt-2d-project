#!/usr/bin/env python3
"""
Synthetic receipt generator for MIE1517 project.
Generates receipt images with ground truth and accurate bounding boxes.
Fixed version that properly handles augmentation and bbox scaling.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import random
from datetime import datetime
import math

from receipt_generator.enhanced_renderer import EnhancedReceiptBuilder
from receipt_generator.templates import TemplateLibrary
from receipt_generator.data_generator import ProductDatabase
from receipt_generator.augmentation import AugmentationPipeline, RealisticEffects
from receipt_generator.styles import ReceiptStyleManager, ReceiptStyle, ReceiptVariations


class SyntheticReceiptGenerator:
    def __init__(self, output_dir: str = "./data/synthetic", seed: Optional[int] = None):
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.annotations_dir = self.output_dir / "annotations"
        self.bbox_dir = self.output_dir / "bboxes"

        self.product_db = ProductDatabase(seed=seed)
        self.builder = EnhancedReceiptBuilder()
        self.augmentation = AugmentationPipeline()
        self.style_manager = ReceiptStyleManager()

        if seed:
            random.seed(seed)

    def generate_receipt(self, receipt_id: str, store_type: str = "grocery") -> Dict:
        # Generate transaction
        transaction = self.product_db.generate_transaction_data(store_type)

        # Create template
        if store_type == "grocery":
            template = TemplateLibrary.grocery_store()
        elif store_type == "restaurant":
            template = TemplateLibrary.restaurant()
        else:
            template = TemplateLibrary.retail_store()

        # Apply style variations
        style = random.choice(list(ReceiptStyle))
        style_settings = self.style_manager.get_style(style)
        template.width = ReceiptVariations.get_random_width()
        template.padding = ReceiptVariations.get_random_margin()
        template.background_color = style_settings.background_color
        template.text_color = style_settings.text_color

        # Build receipt with position tracking
        receipt_img, text_regions = self.builder.build_from_transaction_with_positions(template, transaction)
        original_size = receipt_img.size

        # Apply style effects
        receipt_img = self.style_manager.apply_style_effects(receipt_img, style)

        # Apply augmentations with rotation
        # Store original size before augmentation
        pre_aug_size = receipt_img.size

        # Apply rotation with expand
        angle = random.uniform(-3, 3)
        receipt_img = receipt_img.rotate(angle, expand=True, fillcolor=(255, 255, 255), resample=Image.Resampling.BICUBIC)
        post_rotation_size = receipt_img.size

        # Apply other augmentations
        receipt_img = self.augmentation.apply(receipt_img, ["noise", "blur", "brightness"])

        if random.random() < 0.3:
            receipt_img = RealisticEffects.add_fold_lines(receipt_img, num_folds=random.randint(1, 2))

        # Final size after all augmentations
        final_size = receipt_img.size

        # Update bounding boxes for rotation and size changes
        updated_regions = self._update_bboxes_for_rotation(
            text_regions,
            original_size,
            final_size,
            angle
        )

        # Extract ground truth
        ground_truth = self._extract_ground_truth(transaction, updated_regions)

        # Format bounding boxes
        bbox_data = {"results": self._format_bboxes(updated_regions)}

        # Save files
        self.images_dir.mkdir(exist_ok=True, parents=True)
        self.annotations_dir.mkdir(exist_ok=True, parents=True)
        self.bbox_dir.mkdir(exist_ok=True, parents=True)

        # Save image
        image_path = self.images_dir / f"{receipt_id}.png"
        receipt_img.save(image_path)

        # Save ground truth
        with open(self.annotations_dir / f"{receipt_id}.json", 'w') as f:
            json.dump(ground_truth, f, indent=2)

        # Save bounding boxes
        with open(self.bbox_dir / f"{receipt_id}.json", 'w') as f:
            json.dump(bbox_data, f, indent=2)

        return {
            "id": receipt_id,
            "image": str(image_path),
            "ground_truth": ground_truth,
            "num_boxes": len(bbox_data["results"])
        }

    def _update_bboxes_for_rotation(self, text_regions: List[Dict],
                                   original_size: Tuple[int, int],
                                   final_size: Tuple[int, int],
                                   angle: float) -> List[Dict]:
        """Update bounding boxes for rotation and size change."""

        orig_w, orig_h = original_size
        final_w, final_h = final_size

        # Calculate center points
        cx_old = orig_w / 2
        cy_old = orig_h / 2
        cx_new = final_w / 2
        cy_new = final_h / 2

        # Convert angle to radians (negative because PIL rotates counter-clockwise)
        angle_rad = math.radians(-angle)

        updated_regions = []
        for region in text_regions:
            # Transform each corner point
            new_bbox = []
            for point in region["bbox"]:
                # Original point
                x, y = point[0], point[1]

                # Translate to origin (center of original)
                x_centered = x - cx_old
                y_centered = y - cy_old

                # Apply rotation
                x_rot = x_centered * math.cos(angle_rad) - y_centered * math.sin(angle_rad)
                y_rot = x_centered * math.sin(angle_rad) + y_centered * math.cos(angle_rad)

                # Translate to new image coordinates
                x_new = x_rot + cx_new
                y_new = y_rot + cy_new

                new_bbox.append([x_new, y_new])

            updated_region = region.copy()
            updated_region["bbox"] = new_bbox

            # Expand bbox slightly to ensure all rotated text is captured
            # Calculate bounding rectangle
            xs = [p[0] for p in new_bbox]
            ys = [p[1] for p in new_bbox]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            # Add padding for rotation artifacts
            padding = 2
            updated_region["bbox"] = [
                [min_x - padding, min_y - padding],  # top-left
                [max_x + padding, min_y - padding],  # top-right
                [max_x + padding, max_y + padding],  # bottom-right
                [min_x - padding, max_y + padding]   # bottom-left
            ]

            updated_regions.append(updated_region)

        return updated_regions

    def _extract_ground_truth(self, transaction: Dict, text_regions: List[Dict]) -> Dict:
        ground_truth = {"company": "", "date": "", "address": "", "total": ""}

        # Get company name (first text region typically)
        for region in text_regions:
            text = region["text"].strip()
            if not ground_truth["company"] and len(text) > 3:
                ground_truth["company"] = text
                break

        # Get date
        for region in text_regions:
            text = region["text"].strip()
            if "/" in text and any(c.isdigit() for c in text):
                parts = text.split()
                for part in parts:
                    if "/" in part and len(part.split("/")) == 3:
                        ground_truth["date"] = part
                        break
                if ground_truth["date"]:
                    break

        # Get address
        address_parts = []
        for region in text_regions:
            if region.get("type") == "address":
                address_parts.append(region["text"].strip())
        if address_parts:
            ground_truth["address"] = ", ".join(address_parts)
        else:
            # Fallback
            address_lines = transaction.get("store", {}).get("address", [])
            if isinstance(address_lines, list):
                ground_truth["address"] = ", ".join(address_lines).strip()

        # Get total (largest dollar amount)
        max_amount = 0.0
        for region in text_regions:
            text = region["text"].strip()
            if "$" in text:
                try:
                    amount = float(text.replace("$", "").replace(",", ""))
                    if amount > max_amount:
                        max_amount = amount
                        ground_truth["total"] = f"{amount:.2f}"
                except:
                    pass

        # Fallback for date
        if not ground_truth["date"] and "timestamp" in transaction:
            ground_truth["date"] = transaction["timestamp"].split(" ")[0]

        return ground_truth

    def _format_bboxes(self, text_regions: List[Dict]) -> List[Dict]:
        results = []
        for idx, region in enumerate(text_regions):
            if not region.get("text", "").strip():
                continue
            results.append({
                "box_id": idx,
                "bbox": region["bbox"],  # Already in 4-point format
                "text": region["text"].strip()
            })
        return results

    def generate_batch(self, count: int = 100, store_types: Optional[List[str]] = None):
        if store_types is None:
            store_types = ["grocery", "restaurant", "retail"]

        print(f"Generating {count} receipts...")
        results = []

        for i in range(count):
            receipt_id = f"{i:06d}"
            store_type = store_types[i % len(store_types)]

            try:
                result = self.generate_receipt(receipt_id, store_type)
                results.append(result)

                if (i + 1) % 10 == 0:
                    print(f"  {i + 1}/{count} completed")
            except Exception as e:
                print(f"  Error on receipt {i}: {e}")
                import traceback
                traceback.print_exc()

        print(f"✓ Generated {len(results)} receipts")
        print(f"  Images: {self.images_dir}/")
        print(f"  Ground truth: {self.annotations_dir}/")
        print(f"  Bounding boxes: {self.bbox_dir}/")

        return results


def generate(count: int = 100, output_dir: str = "./data/synthetic", seed: Optional[int] = None):
    """Main API function."""
    generator = SyntheticReceiptGenerator(output_dir, seed)
    return generator.generate_batch(count)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic receipts")
    parser.add_argument("--count", type=int, default=10, help="Number of receipts")
    parser.add_argument("--output", type=str, default="./data/synthetic", help="Output directory")
    parser.add_argument("--seed", type=int, help="Random seed")

    args = parser.parse_args()
    generate(args.count, args.output, args.seed)