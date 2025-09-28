# 2D Receipt Generator

A clean, modular Python library for generating synthetic receipt images with matched text/metadata for OCR training.

## Features

- **Multiple store types**: Grocery stores, restaurants, and retail stores
- **5 Receipt styles**: Thermal, inkjet, dot matrix, modern POS, and carbon copy styles
- **Realistic augmentation**: Rotation, minimal blur, noise, perspective distortion, fold lines, coffee stains
- **Format variations**: Random widths (280-400px), margins, and layouts for natural variety
- **Perfect ground truth**: Exact text positions and content in metadata
- **Multiple export formats**: Tesseract, YOLO, COCO for different OCR systems
- **Highly customizable**: Templates, products, styles, and augmentation parameters

## Installation

```bash
# Create conda environment
conda create -n receipt-generator python=3.10 -y
conda activate receipt-generator

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Generate a single receipt preview
```bash
python generate_receipts.py --preview
```

### Generate a batch of receipts
```bash
python generate_receipts.py --count 100 --output-dir training_data
```

### Generate without augmentation (clean receipts)
```bash
python generate_receipts.py --count 50 --no-augmentation
```

### Generate specific store types
```bash
python generate_receipts.py --count 30 --store-types grocery restaurant
```

### Export for OCR training
```bash
python generate_receipts.py --count 100 --export-format tesseract
```

## Python API Usage

```python
from receipt_generator import ReceiptGenerator
from receipt_generator.styles import ReceiptStyle

# Initialize generator
generator = ReceiptGenerator(output_dir="output", enable_augmentation=True)

# Generate single receipt with specific style
image, metadata = generator.generate_single(
    store_type="grocery",
    style=ReceiptStyle.THERMAL  # or INKJET, DOT_MATRIX, MODERN_POS, CARBON_COPY
)

# Generate batch with random styles
results = generator.generate_batch(count=100, store_types=["grocery", "restaurant"])

# Export for OCR training
generator.export_for_ocr_training(results, format="tesseract")
```

## Project Structure

```
receipt_generator/
├── templates.py        # Receipt layout and structure definitions
├── data_generator.py   # Product database and random data generation
├── renderer.py        # PIL-based receipt rendering engine
├── augmentation.py    # Image augmentation and realistic effects
├── styles.py          # Receipt styles (thermal, inkjet, dot matrix, etc.)
└── generator.py       # Main generator class and export functionality
```

## Customization

### Adding new store types
Edit `data_generator.py` to add new product lists and store names.

### Modifying receipt layouts
Edit `templates.py` to create custom receipt templates with different layouts.

### Adding new receipt styles
Edit `styles.py` to add new printer styles and effects (e.g., faded thermal, worn dot matrix).

### Adjusting augmentation
Edit parameters in `augmentation.py` or pass custom settings to `AugmentationPipeline`. Default blur is minimal (0-0.5 range) for clearer OCR training data.

## Output Format

Each generated receipt includes:
- **Image**: PNG file with the receipt
- **Metadata**: JSON file with:
  - Complete text content
  - Item details and prices
  - Text region positions
  - Transaction details

## Integration with OCR Training

For real-world OCR training:
1. Generate synthetic receipts with this tool
2. Use a document rectification tool (OpenCV, DocTR) to preprocess real photos
3. Train your OCR model on the consistent, flat receipt images
4. Apply the same rectification to user photos before inference

This approach ensures your model trains and infers on similar-looking flat, corrected images.