#!/usr/bin/env python3
"""
Quick demo of the receipt generator with bounding box visualization.
"""

import json
from pathlib import Path
from generate_synthetic_receipts import generate
from visualize_bbox import visualize_batch


def main():
    print("=" * 60)
    print("Receipt Generator Demo")
    print("=" * 60)

    # Generate 5 sample receipts
    print("\n1. Generating 5 sample receipts...")
    results = generate(count=5, output_dir="./demo_output", seed=42)

    # Show sample outputs
    print("\n2. Sample outputs:")
    data_dir = Path("./demo_output")

    # Show a ground truth example
    with open(data_dir / "annotations" / "000000.json", 'r') as f:
        gt = json.load(f)
        print(f"\n   Ground Truth (000000.json):")
        print(f"   - Company: {gt['company']}")
        print(f"   - Date: {gt['date']}")
        print(f"   - Address: {gt['address']}")
        print(f"   - Total: ${gt['total']}")

    # Show a bounding box example
    with open(data_dir / "bboxes" / "000000.json", 'r') as f:
        bbox_data = json.load(f)
        print(f"\n   Bounding Boxes: {len(bbox_data['results'])} text regions")
        print(f"   First 3 boxes:")
        for box in bbox_data["results"][:3]:
            print(f"   - Box {box['box_id']}: '{box['text']}'")

    # Visualize bounding boxes
    print("\n3. Creating visualizations...")
    visualize_batch("./demo_output", count=3)

    print("\n✓ Demo complete!")
    print(f"  Check ./demo_output/ for generated files")
    print(f"  Check ./demo_output/visualizations/ for bbox visualizations")


if __name__ == "__main__":
    main()