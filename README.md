# Receipt Generator for MIE1517

Synthetic receipt generator with accurate ground truth and bounding boxes for training receipt OCR models.

## Installation

```bash
# Use conda environment
conda activate receipt-generator

# Or install requirements
pip install -r requirements.txt
```

## Quick Start

### Generate Receipts

```python
from generate_synthetic_receipts import generate

# Generate 1000 grocery receipts (most common use case)
generate(count=1000, output_dir="./data/synthetic", seed=42)
```

Or via command line:
```bash
python generate_synthetic_receipts.py --count 1000 --output ./data/synthetic
```

## Sample Generated Receipt

<table>
<tr>
<td>Original Receipt</td>
<td>With Bounding Boxes (CV2 Style)</td>
</tr>
<tr>
<td><img src="samples/synthetic/images/000001.png" width="300"></td>
<td><img src="samples/synthetic/visualizations/viz_000001.png" width="300"></td>
</tr>
</table>

**Sample data files:**
- Ground truth: `samples/synthetic/annotations/000001.json`
- Bounding boxes: `samples/synthetic/bboxes/000001.json`

**To regenerate samples:** Run `python regenerate_samples.py`

## Output Structure

```
samples/synthetic/
├── images/          # Receipt images (*.png)
├── annotations/     # Ground truth JSON (company, date, address, total)
└── bboxes/          # Bounding boxes JSON (with text and coordinates)
```

## Generating Different Receipt Varieties

```python
from generate_synthetic_receipts import SyntheticReceiptGenerator

# Initialize generator
generator = SyntheticReceiptGenerator(output_dir="./data", seed=42)

# Generate specific store types
# Grocery stores (most common - supermarkets, convenience stores)
generator.generate_receipt("receipt_001", store_type="grocery")

# Restaurants (sit-down, fast food, cafes)
generator.generate_receipt("receipt_002", store_type="restaurant")

# Retail stores (clothing, electronics, general merchandise)
generator.generate_receipt("receipt_003", store_type="retail")

# Mixed batch generation
results = generator.generate_batch(
    count=1000,
    store_types=["grocery", "grocery", "grocery", "restaurant", "retail"]  # 60% grocery
)
```

### Store Type Examples

- **Grocery**: FreshMart, SuperSave, Green Grocer, QuickStop Market
  - Items: Milk, Eggs, Bread, Produce, Snacks
  - Typical total: $20-$150

- **Restaurant**: The Golden Fork, Urban Eats, Blue Moon Cafe
  - Items: Entrees, Appetizers, Beverages, Desserts
  - Typical total: $30-$200

- **Retail**: Fashion Forward, Style House, Urban Outfitters
  - Items: Clothing, Accessories, Footwear
  - Typical total: $50-$500

## Visualize Bounding Boxes

```bash
# Visualize specific receipt
python visualize_bbox.py --id 000001 --data ./data/synthetic

# Visualize batch
python visualize_bbox.py --count 5 --data ./data/synthetic
```

Visualizations are saved to `data/synthetic/visualizations/`.

## Integration with MIE1517 Project

```python
import sys
sys.path.append('./receipt-2d-project')
from generate_synthetic_receipts import generate

# Generate training data (mostly grocery receipts)
results = generate(count=1000, output_dir="./data/synthetic", seed=42)

# Load for training
import json
from pathlib import Path

receipt_id = "000001"
image_path = f"./data/synthetic/images/{receipt_id}.png"

# Load ground truth
with open(f"./data/synthetic/annotations/{receipt_id}.json") as f:
    ground_truth = json.load(f)

# Load bounding boxes
with open(f"./data/synthetic/bboxes/{receipt_id}.json") as f:
    bbox_data = json.load(f)

# Access data
for box in bbox_data["results"]:
    print(f"Text: {box['text']}, Box: {box['bbox']}")
```

## Features

- **Accurate Bounding Boxes**: Positions match actual rendered text with rotation support
- **No OCR Required**: Ground truth generated directly
- **Store Variety**: Grocery (most common), restaurant, and retail receipts
- **Realistic Effects**: Noise, blur, fold lines, rotations (-3° to +3°)
- **Fast Generation**: ~100 receipts per minute
- **CV2-style Visualization**: Green bounding boxes with red text labels

## API Reference

```python
from generate_synthetic_receipts import SyntheticReceiptGenerator

# Initialize generator
generator = SyntheticReceiptGenerator(
    output_dir="./data",
    seed=42  # For reproducibility
)

# Generate single receipt
result = generator.generate_receipt(
    receipt_id="test001",
    store_type="grocery"  # Options: "grocery", "restaurant", "retail"
)

# Generate batch with custom distribution
results = generator.generate_batch(
    count=1000,
    store_types=["grocery"] * 7 + ["restaurant"] * 2 + ["retail"] * 1  # 70% grocery, 20% restaurant, 10% retail
)
```