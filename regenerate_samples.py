#!/usr/bin/env python3
"""
Script to regenerate sample images for README documentation.
Run this whenever you need to update the sample images.
"""

from pathlib import Path
from generate_synthetic_receipts import SyntheticReceiptGenerator
from visualize_bbox import visualize_receipt


def regenerate_samples():
    """Regenerate sample receipt images for documentation."""

    print("Regenerating sample images...")
    print("=" * 60)

    # Generate sample receipt with ID 000001 and fixed seed for consistency
    generator = SyntheticReceiptGenerator('./samples/synthetic', seed=123)
    result = generator.generate_receipt('000001', 'grocery')

    print(f"✓ Generated sample receipt: {result['id']}")
    print(f"  Image: samples/synthetic/images/000001.png")
    print(f"  Ground truth: samples/synthetic/annotations/000001.json")
    print(f"  Bounding boxes: samples/synthetic/bboxes/000001.json")

    # Create visualization using the normal process
    output_dir = Path('./samples/synthetic/visualizations')
    output_dir.mkdir(exist_ok=True)

    visualize_receipt('000001', './samples/synthetic', './samples/synthetic/visualizations/viz_000001.png')
    print(f"✓ Created visualization: samples/synthetic/visualizations/viz_000001.png")

    print("\n" + "=" * 60)
    print("Sample images regenerated successfully!")
    print("\nFiles for README:")
    print("  Original: samples/synthetic/images/000001.png")
    print("  With BBoxes: samples/synthetic/visualizations/viz_000001.png")
    print("  Ground Truth: samples/synthetic/annotations/000001.json")
    print("  BBoxes: samples/synthetic/bboxes/000001.json")
    print("\nThese paths are referenced in the README.md")


if __name__ == "__main__":
    regenerate_samples()