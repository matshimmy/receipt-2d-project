#!/usr/bin/env python3

from receipt_generator import ReceiptGenerator
from receipt_generator.styles import ReceiptStyle
from PIL import Image
import os

def main():
    generator = ReceiptGenerator(output_dir="showcase", enable_augmentation=False)

    styles = [
        (ReceiptStyle.THERMAL, "Thermal printer style"),
        (ReceiptStyle.INKJET, "Inkjet printer style"),
        (ReceiptStyle.DOT_MATRIX, "Dot matrix style"),
        (ReceiptStyle.MODERN_POS, "Modern POS system"),
        (ReceiptStyle.CARBON_COPY, "Carbon copy style")
    ]

    images = []

    for style, description in styles:
        print(f"Generating {description}...")

        # Generate receipt with specific style
        img, metadata = generator.generate_single(
            store_type="grocery",
            style=style,
            augmentations=[]  # No augmentation to show clean styles
        )

        # Save individual style
        filename = f"showcase_{style.value}.png"
        img.save(filename)
        print(f"  Saved as {filename}")

        images.append(img)

    # Create a combined showcase image
    print("\nCreating combined showcase image...")

    # Calculate combined image size
    max_height = max(img.height for img in images)
    total_width = sum(img.width for img in images) + (len(images) - 1) * 20  # 20px spacing

    # Create combined image
    combined = Image.new('RGB', (total_width, max_height), (240, 240, 240))

    x_offset = 0
    for img in images:
        combined.paste(img, (x_offset, 0))
        x_offset += img.width + 20

    combined.save("showcase_all_styles.png")
    print("Combined showcase saved as showcase_all_styles.png")

    # Generate augmented examples
    print("\nGenerating augmented examples...")

    # Re-enable augmentation
    from receipt_generator.augmentation import AugmentationPipeline
    generator.enable_augmentation = True
    generator.augmentation = AugmentationPipeline(blur_range=(0, 0.3))

    augmented_imgs = []
    for i in range(3):
        img, _ = generator.generate_single(
            store_type=["grocery", "restaurant", "retail"][i]
        )
        img.save(f"showcase_augmented_{i+1}.png")
        augmented_imgs.append(img)
        print(f"  Saved augmented example {i+1}")

    print("\nShowcase generation complete!")
    print("Files generated:")
    print("- showcase_thermal.png")
    print("- showcase_inkjet.png")
    print("- showcase_dot_matrix.png")
    print("- showcase_modern_pos.png")
    print("- showcase_carbon_copy.png")
    print("- showcase_all_styles.png (combined)")
    print("- showcase_augmented_1.png")
    print("- showcase_augmented_2.png")
    print("- showcase_augmented_3.png")

if __name__ == "__main__":
    main()