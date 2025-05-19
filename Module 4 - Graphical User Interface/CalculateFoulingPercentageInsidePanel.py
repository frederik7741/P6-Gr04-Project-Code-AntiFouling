import cv2
import json
import numpy as np
import os
from glob import glob

# ---- CONFIG ----
main_json_dir = r'/Labelled Data - Detect Fouling'
image_root_dir = r'/Interactive Interface/Panel Images'
output_json_file = 'Interactive Interface/fouling_percentages_inside_panel.json'
results = {}

# Function to find corresponding image path recursively
def find_image_recursively(root_dir, base_name):
    possible_extensions = ['.png', '.jpg', '.jpeg']
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isfile(item_path):
            name, ext = os.path.splitext(item)
            if name == base_name and ext.lower() in possible_extensions:
                return item_path
        elif os.path.isdir(item_path):
            found = find_image_recursively(item_path, base_name)
            if found:
                return found
    return None

# Find all JSON files
json_files = glob(os.path.join(main_json_dir, '**', '*.json'), recursive=True)

for json_path in json_files:
    base_name = os.path.splitext(os.path.basename(json_path))[0]
    print(f"\nProcessing JSON: {base_name}")

    # Find the corresponding image
    image_path = find_image_recursively(image_root_dir, base_name)

    if image_path is None:
        print(f"  Warning: Could not find corresponding image for {base_name}.json in {image_root_dir} or its subfolders.")
        continue

    print(f"  Found image: {image_path}")

    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"    Warning: Could not load image {image_path}")
        continue

    height, width = image.shape[:2]

    # Create empty masks
    panel_mask = np.zeros((height, width), dtype=np.uint8)
    fouling_mask = np.zeros((height, width), dtype=np.uint8)
    none_mask = np.zeros((height, width), dtype=np.uint8)

    # Load annotation
    with open(json_path, 'r') as f:
        data = json.load(f)

    for shape in data.get("shapes", []):
        label = shape["label"]
        points = np.array(shape["points"], dtype=np.float32)

        # Convert points to integers and clip to image bounds
        points = np.round(points).astype(np.int32)
        points = points.reshape((-1, 1, 2))
        points[:, :, 0] = np.clip(points[:, :, 0], 0, width - 1)
        points[:, :, 1] = np.clip(points[:, :, 1], 0, height - 1)

        if points.size > 0:
            if label == "panel":
                cv2.fillPoly(panel_mask, [points], 255)
            elif label == "fouling":
                cv2.fillPoly(fouling_mask, [points], 255)
            elif label == "none":
                cv2.fillPoly(none_mask, [points], 255)
            else:
                print(f"    Warning: Unknown label '{label}'")

    # Create union of panel and none
    total_area_mask = cv2.bitwise_or(panel_mask, none_mask)

    # Fouling inside the valid area (panel + none)
    fouling_inside_total = cv2.bitwise_and(fouling_mask, total_area_mask)

    # Clean area = total area - fouling pixels (to avoid overlap)
    clean_area_mask = cv2.bitwise_and(total_area_mask, cv2.bitwise_not(fouling_mask))

    # Count pixels
    fouling_pixels = np.sum(fouling_inside_total == 255)
    clean_pixels = np.sum(clean_area_mask == 255)
    total_pixels = fouling_pixels + clean_pixels

    # Calculate fouling percentage
    fouling_percentage = (fouling_pixels / total_pixels) * 100 if total_pixels > 0 else 0.0

    print(f"    Fouling percentage within panel: {fouling_percentage:.2f}%")
    results[base_name] = fouling_percentage

# Save results to JSON
with open(output_json_file, 'w') as f:
    json.dump(results, f, indent=4)

print(f"\nFouling percentages saved to {output_json_file}")
