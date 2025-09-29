#!/usr/bin/env python3
"""Generate sample receipts showing different styles and variations."""

from PIL import Image
import os
import random
from receipt_generator import ReceiptGenerator
from receipt_generator.templates import ReceiptTemplate, TemplateLibrary

def generate_sample_grid():
    """Generate a grid of sample receipts showing different variations."""

    # Create generator with augmentation disabled for clean samples
    generator = ReceiptGenerator(
        output_dir="samples_temp",
        enable_augmentation=False  # Clean samples to show variations clearly
    )

    # Generate receipts with different store types and ensure width variation
    store_types = ["grocery", "restaurant", "retail", "pharmacy", "electronics", "bookstore"]

    # Vary the width for each receipt to show that capability
    widths = [280, 300, 320, 350, 380, 400]

    print(f"Generating {len(store_types)} sample receipts with different styles and widths...")

    # Generate receipts and collect images
    images = []
    for i, (store_type, width) in enumerate(zip(store_types, widths)):
        # Create a template with specified width
        if store_type in ["grocery", "pharmacy"]:
            template = TemplateLibrary.grocery_store()
        elif store_type == "restaurant":
            template = TemplateLibrary.restaurant()
        else:
            template = TemplateLibrary.retail_store()

        # Set the width for this receipt
        template.width = width

        # Generate single receipt with the custom template
        image, metadata = generator.generate_single(
            store_type=store_type,
            template=template
        )

        if image:
            images.append(image)
            print(f"  Generated {i+1}/{len(store_types)}: {store_type} (width: {width}px)")
        else:
            print(f"  Warning: Could not generate image for {store_type}")

    if images:
        # Find max dimensions for normalization
        max_width = max(img.width for img in images)
        max_height = max(img.height for img in images)

        # Create normalized images (center them in a fixed-size box)
        normalized_images = []
        for img in images:
            # Create a white background of max size
            normalized = Image.new('RGB', (max_width, max_height), (255, 255, 255))
            # Center the receipt in this box
            x_offset = (max_width - img.width) // 2
            y_offset = 0  # Top-align receipts
            normalized.paste(img, (x_offset, y_offset))
            normalized_images.append(normalized)

        # Create a 3x2 grid
        padding = 20
        composite_width = max_width * 3 + padding * 4
        composite_height = max_height * 2 + padding * 3

        # Light gray background
        composite = Image.new('RGB', (composite_width, composite_height), (240, 240, 240))

        # Place images in grid
        for i, img in enumerate(normalized_images[:6]):
            row = i // 3
            col = i % 3
            x = padding + col * (max_width + padding)
            y = padding + row * (max_height + padding)
            composite.paste(img, (x, y))

        # Save the composite
        composite.save('samples.png')
        print(f'\nSuccessfully created samples.png with {len(images)} receipts')
        print(f'Image saved as: {os.path.abspath("samples.png")}')

        # Clean up temporary directory if it exists
        import shutil
        if os.path.exists('samples_temp'):
            shutil.rmtree('samples_temp')
            print("Cleaned up temporary files")
    else:
        print("\nError: No images were generated successfully")

    return images

if __name__ == "__main__":
    # Generate main samples showing style and width variations
    images = generate_sample_grid()

    if images:
        print("\nSample generation complete!")
        print("The samples.png file shows:")
        print("- Different store types (grocery, restaurant, retail, etc.)")
        print("- Various receipt widths (280px to 400px)")
        print("- Random header styles (minimal, compact, detailed, centered)")
        print("- Random footer styles (minimal, compact, spread, standard, detailed)")
        print("- Different fonts and printer styles")
    else:
        print("\nSample generation failed - please check for errors above")