import json
import cv2
from pathlib import Path
from typing import Dict, Optional


def upscale_bboxes_for_image(image_path: Path, bbox_data: Dict, target_width: int = 2000) -> Dict:
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    original_width = img.shape[1]
    upscale_factor = target_width / original_width if original_width < target_width else 1.0
    
    if upscale_factor == 1.0:
        return bbox_data
    
    upscaled_results = []
    for box in bbox_data.get("results", []):
        upscaled_bbox = [
            [point[0] * upscale_factor, point[1] * upscale_factor]
            for point in box["bbox"]
        ]
        upscaled_box = box.copy()
        upscaled_box["bbox"] = upscaled_bbox
        upscaled_results.append(upscaled_box)
    
    return {"results": upscaled_results}


def upscale_bbox_file(bbox_path: Path, image_path: Path, output_path: Optional[Path] = None, 
                      target_width: int = 2000) -> Dict:
    with open(bbox_path, 'r') as f:
        bbox_data = json.load(f)
    
    upscaled_data = upscale_bboxes_for_image(image_path, bbox_data, target_width)
    
    output = output_path if output_path else bbox_path
    with open(output, 'w') as f:
        json.dump(upscaled_data, f, indent=2)
    
    return upscaled_data


def upscale_all_bboxes(bbox_dir: Path, images_dir: Path, output_dir: Optional[Path] = None,
                      target_width: int = 2000):
    bbox_dir = Path(bbox_dir)
    images_dir = Path(images_dir)
    
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
    
    json_files = list(bbox_dir.glob("*.json"))
    
    for bbox_path in json_files:
        receipt_id = bbox_path.stem
        image_path = images_dir / f"{receipt_id}.png"
        
        if not image_path.exists():
            continue
        
        img = cv2.imread(str(image_path))
        if img is None:
            continue
        
        output_path = output_dir / bbox_path.name if output_dir else None
        upscale_bbox_file(bbox_path, image_path, output_path, target_width)
    
    print(f"✓ Processed {len(json_files)} bbox files")


def upscale_synthetic_bboxes(data_dir: str = "./data/synthetic", 
                             bbox_dir: Optional[str] = None,
                             output_dir: Optional[str] = None,
                             target_width: int = 2000):
    data_dir = Path(data_dir)
    images_dir = data_dir / "images"
    
    if bbox_dir:
        bbox_dir = Path(bbox_dir)
    else:
        bbox_dir = data_dir / "bboxes"
    
    upscale_all_bboxes(bbox_dir, images_dir, 
                      Path(output_dir) if output_dir else None,
                      target_width)
