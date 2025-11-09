#!/usr/bin/env python3
"""
Visualize bounding boxes on receipt images using CV2 style.
"""

import json
from pathlib import Path
import cv2
import numpy as np


def visualize_receipt(receipt_id: str, data_dir: str = "./data/synthetic", bbox_dir: str = None, output_path: str = None):
    """Draw bounding boxes on a receipt image using CV2 style."""

    data_dir = Path(data_dir)
    
    # Determine bbox directory
    if bbox_dir is not None:
        bbox_dir = Path(bbox_dir)
    else:
        bbox_dir = data_dir / "bboxes"

    # Load image
    img_path = data_dir / "images" / f"{receipt_id}.png"
    if not img_path.exists():
        print(f"Image not found: {img_path}")
        return None

    # Read image with CV2
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"Failed to load image: {img_path}")
        return None

    # Load bounding boxes
    bbox_path = bbox_dir / f"{receipt_id}.json"
    if not bbox_path.exists():
        print(f"Bounding boxes not found: {bbox_path}")
        return None

    with open(bbox_path, 'r') as f:
        bbox_data = json.load(f)

    # Draw each bounding box
    for box in bbox_data["results"]:
        bbox = box["bbox"]
        text = box["text"]

        # Convert 4 corner points to rectangle
        # Find min/max coordinates
        xs = [p[0] for p in bbox]
        ys = [p[1] for p in bbox]
        x1, y1 = int(min(xs)), int(min(ys))
        x2, y2 = int(max(xs)), int(max(ys))

        # Draw green rectangle (BGR format in CV2)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green color, thickness 2

        # Add text label above the box - let it go off-screen if needed
        # OpenCV will still render the visible portion
        text_y = y1 - 5  # Small padding above the box
        cv2.putText(img, text[:20], (x1, text_y),  # Truncate long text
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)  # Red text (BGR format)

    # Save or display
    if output_path:
        cv2.imwrite(str(output_path), img)
        print(f"Saved visualization to: {output_path}")
    else:
        cv2.imshow("Receipt with Bounding Boxes", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return img


def visualize_batch(data_dir: str = "./data/synthetic", bbox_dir: str = None, count: int = 5):
    """Visualize multiple receipts."""

    data_dir = Path(data_dir)
    output_dir = data_dir / "visualizations"
    output_dir.mkdir(exist_ok=True)

    # Find available receipts
    images = sorted((data_dir / "images").glob("*.png"))[:count]

    if not images:
        print("No receipts found to visualize")
        return

    print(f"Visualizing {len(images)} receipts...")

    for img_path in images:
        receipt_id = img_path.stem
        output_path = output_dir / f"viz_{receipt_id}.png"
        visualize_receipt(receipt_id, data_dir, bbox_dir, output_path)

    print(f"✓ Visualizations saved to: {output_dir}/")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Visualize receipt bounding boxes")
    parser.add_argument("--id", type=str, help="Specific receipt ID to visualize")
    parser.add_argument("--data", type=str, default="./data/synthetic", help="Data directory")
    parser.add_argument("--bbox-dir", type=str, default=None, help="Bounding box directory (if not specified, uses data_dir/bboxes)")
    parser.add_argument("--count", type=int, default=5, help="Number to visualize (batch mode)")
    parser.add_argument("--output", type=str, help="Output path for visualization")

    args = parser.parse_args()

    if args.id:
        visualize_receipt(args.id, args.data, args.bbox_dir, args.output)
    else:
        visualize_batch(args.data, args.bbox_dir, args.count)