#!/usr/bin/env python3

import argparse
from receipt_generator import ReceiptGenerator
from PIL import Image
import json


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic receipt images for OCR training")

    parser.add_argument("--count", type=int, default=10,
                       help="Number of receipts to generate (default: 10)")

    parser.add_argument("--output-dir", type=str, default="output",
                       help="Output directory for generated receipts (default: output)")

    parser.add_argument("--store-types", nargs="+", default=["grocery", "restaurant", "retail"],
                       help="Store types to generate (default: grocery restaurant retail)")

    parser.add_argument("--no-augmentation", action="store_true",
                       help="Disable image augmentation")

    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")

    parser.add_argument("--preview", action="store_true",
                       help="Generate and display a single receipt preview")

    args = parser.parse_args()

    # Initialize generator
    generator = ReceiptGenerator(
        output_dir=args.output_dir,
        enable_augmentation=not args.no_augmentation,
        seed=args.seed
    )

    if args.preview:
        # Generate single preview
        print("Generating preview receipt...")
        img, metadata = generator.generate_single(store_type=args.store_types[0])

        # Save preview
        img.save("preview.png")
        with open("preview_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"Preview saved to preview.png")
        print(f"Metadata saved to preview_metadata.json")

        # Display some info
        print(f"\nReceipt Details:")
        print(f"Store: {metadata['store']['name']}")
        print(f"Items: {len(metadata['items'])}")
        print(f"Total: ${metadata['totals']['total']:.2f}")

    else:
        # Generate batch
        print(f"Generating {args.count} receipts...")
        results = generator.generate_batch(
            count=args.count,
            store_types=args.store_types,
            save=True
        )

        print(f"\nGenerated {len(results)} receipts")
        print(f"Output directory: {args.output_dir}")

        print("\nGeneration complete!")
        print(f"- Images saved to: {args.output_dir}/images/")
        print(f"- Metadata saved to: {args.output_dir}/metadata/")
        print(f"- Summary saved to: {args.output_dir}/generation_summary.json")


if __name__ == "__main__":
    main()