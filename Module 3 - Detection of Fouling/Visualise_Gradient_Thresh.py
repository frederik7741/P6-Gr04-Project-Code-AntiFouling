import cv2
import numpy as np
import json
import matplotlib.pyplot as plt
import os
from PIL import Image, ImageDraw
from scipy.ndimage import generic_filter
import matplotlib.colors
from numpy.lib.stride_tricks import as_strided


def calculate_similarity_with_as_strided(image_uint8, window_size, comparison_threshold):
    H, W = image_uint8.shape
    pad_offset = window_size // 2

    # Pad the image (mode='reflect' matches generic_filter's default for this)
    # If image_uint8 is uint8, padded_image will also be uint8.
    padded_image = np.pad(image_uint8, pad_width=pad_offset, mode='reflect')
    
    # Create a strided view of the padded image.
    sH, sW = padded_image.strides
    strided_windows_view = as_strided(
        padded_image,
        shape=(H, W, window_size, window_size),
        strides=(sH, sW, sH, sW)
    )
    
    # Get the center pixel value for each window from the original image.
    # Reshape for broadcasting with strided_windows_view.
    center_pixel_values_view = image_uint8[:, :, np.newaxis, np.newaxis]

    # --- CRITICAL STEP: Cast to float64 (or a sufficiently large signed int) BEFORE subtraction ---
    # This mimics generic_filter's internal promotion of uint8 data to float64.
    strided_windows_float = strided_windows_view.astype(np.float64)
    center_values_float = center_pixel_values_view.astype(np.float64)
    
    # 1. Handle the "if np.all(values == 0): return 0" condition:
    #    generic_filter would pass the float64 window to this check.
    is_window_all_zero = np.all(strided_windows_float == 0.0, axis=(2, 3))

    # 2. Calculate absolute differences using float arithmetic
    abs_differences = np.abs(strided_windows_float - center_values_float)
    
    # 3. Count similar neighbors
    similarity_mask = abs_differences <= comparison_threshold
    similarity_counts = np.sum(similarity_mask, axis=(2, 3))
    
    # 4. Combine results: if window was all zeros, count is 0, otherwise it's the calculated similarity_counts.
    final_counts = np.where(is_window_all_zero, 0, similarity_counts)
    
    return final_counts.astype(np.int32) # Counts are integers

def compute_iou_pixel_count(gt, pt):
    mask1_pixels = np.count_nonzero(gt)
    mask2_pixels = np.count_nonzero(pt)
    intersection_pixels = np.count_nonzero(np.logical_and(gt, pt))
    union_pixels = mask1_pixels + mask2_pixels - intersection_pixels

    if union_pixels == 0:
        return 0.0  # Avoid division by zero

    return intersection_pixels / union_pixels

def determine_if_fouling_dict(similarity_raw_count):
    if 20 <= similarity_raw_count:
        return True
    return False

def count_similar_neighbors(values, threshold=5):
    if np.all(values == 0):
        return 0
    center = values[len(values) // 2]
    return np.sum(np.abs(values - center) <= threshold)

def get_image_with_json(image_path, json_path):
    image = cv2.imread(image_path)
    data = None
    with open(json_path, 'r') as f:
        data = json.load(f)
    return image, data

def get_rgb_heatmap_color(value_normalized):
    value_normalized = np.clip(value_normalized, 0, 1)
    r, g, b = 0, 0, 0
    if value_normalized < 0.25:
        t = value_normalized * 4
        r, g, b = 0, int(t * 255), 255
    elif value_normalized < 0.5:
        t = (value_normalized - 0.25) * 4
        r, g, b = 0, 255, int((1 - t) * 255)
    elif value_normalized < 0.75:
        t = (value_normalized - 0.5) * 4
        r, g, b = int(t * 255), 255, 0
    else:
        t = (value_normalized - 0.75) * 4
        r, g, b = 255, int((1 - t) * 255), 0
    return r, g, b

image_path = "Eval Images/Month_1/AC1_month_1.png" # Example path
json_path = "Labelled Data - Detect Fouling/Labelled Data Month 1 - 10/AC1_month_1.json" # Example path

if not os.path.exists(image_path):
    print(f"Error: Image path not found: {image_path}")
    exit()
if not os.path.exists(json_path):
    print(f"Error: JSON path not found: {json_path}")
    exit()

image, data = get_image_with_json(image_path, json_path)
height, width = image.shape[:2]

gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

panel_mask_img = Image.new("L", (width, height), 0)
fouling_mask_img = Image.new("L", (width, height), 0)
none_mask_img = Image.new("L", (width, height), 0)

draw_panel = ImageDraw.Draw(panel_mask_img)
draw_fouling = ImageDraw.Draw(fouling_mask_img)
draw_none = ImageDraw.Draw(none_mask_img)

for shape in data['shapes']:
    label = shape['label'].lower()
    points = [tuple(p) for p in shape['points']]
    if len(points) >= 2:
        if label == 'panel':
            draw_panel.polygon(points, fill=1)
        elif label == 'fouling':
            draw_fouling.polygon(points, fill=1)
        elif label == 'none':
            draw_none.polygon(points, fill=1)

panel_mask_np = np.array(panel_mask_img)
fouling_mask_np = np.array(fouling_mask_img)
none_mask_np = np.array(none_mask_img)

fouling_mask_filtered = np.logical_and(fouling_mask_np == 1, none_mask_np == 0)

sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
gradient_magnitude = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
if gradient_magnitude.max() > 0:
    gradient_magnitude = (gradient_magnitude / gradient_magnitude.max()) * 255
else:
    gradient_magnitude = np.zeros_like(gradient_magnitude)
grad = gradient_magnitude.astype(np.uint8)

panel_boolean_mask = (panel_mask_np == 1)
grad_on_panel_display = np.zeros_like(grad)
grad_on_panel_display[panel_boolean_mask] = grad[panel_boolean_mask]

adjusted_grad_display = grad_on_panel_display.copy()
adjusted_grad_display[adjusted_grad_display > 50] = 255
mask_0_50 = (grad_on_panel_display <= 50)
original_values_0_50 = grad_on_panel_display[mask_0_50]
adjusted_grad_display[mask_0_50] = (original_values_0_50 / 50.0) * 255
adjusted_grad_display = adjusted_grad_display.astype(np.uint8)

print("Starting similarity count...")
similarity_count = calculate_similarity_with_as_strided(gradient_magnitude, 
                                                window_size=5, 
                                                comparison_threshold=5)
print("Finished similarity count")

kernel_filter_size = 5
kernel_area = float(kernel_filter_size * kernel_filter_size)

output_mask_fouling = np.zeros_like(grad, dtype=np.uint8)
output_mask_non_fouling = np.zeros_like(grad, dtype=np.uint8)
panel_coords_y, panel_coords_x = np.where(panel_boolean_mask)

print("Processing panel coordinates for fouling detection mask...")
count_threshold_met = 0
for i in range(len(panel_coords_y)):
    y = panel_coords_y[i]
    x = panel_coords_x[i]
    raw_similarity = similarity_count[y, x]
    if determine_if_fouling_dict(raw_similarity):
        # count_threshold_met += 1
        output_mask_non_fouling[y, x] = 255
    else:
        output_mask_fouling[y, x] = 255
        count_threshold_met += 1

iou = compute_iou_pixel_count(fouling_mask_filtered, output_mask_fouling)

print("Finished processing panel coordinates for fouling detection mask.")
print(f"Finished processing. {count_threshold_met} pixels met the fouling threshold criteria.")
print(f"IOU with ground truth: {iou:.2f}")

print("Generating heatmap image...")
max_similarity_raw_count = kernel_area
normalized_similarity_on_panel = np.zeros((height, width), dtype=float)

for i in range(len(panel_coords_y)):
    y = panel_coords_y[i]
    x = panel_coords_x[i]
    similarity_value_raw = similarity_count[y, x]
    normalized_similarity_on_panel[y,x] = similarity_value_raw / max_similarity_raw_count

cmap_colors = [(0, 0, 1), (0, 1, 0), (1, 0, 0)]
cmap_nodes = [0.0, 0.5, 1.0]
custom_cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
    "custom_heatmap_cmap", list(zip(cmap_nodes, cmap_colors))
)

plt.figure(figsize=(18, 6))

plt.subplot(1, 2, 1)
if len(image.shape) == 3:
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
else:
    plt.imshow(image, cmap='gray')
plt.title("Original Image")
plt.axis('off')

# plt.subplot(1, 4, 2)
# plt.imshow(output_mask_fouling, cmap='gray')
# plt.title("Fouling Detected Mask")
# plt.axis('off')

# plt.subplot(1, 4, 3)
# plt.imshow(fouling_mask_filtered, cmap='gray')
# plt.title("Fouling Mask Ground Truth")


plt.subplot(1, 2, 2)
im = plt.imshow(normalized_similarity_on_panel, cmap=custom_cmap, vmin=0, vmax=1)
plt.title("Similarity Heatmap on Panel")
plt.axis('off')
cbar = plt.colorbar(im, ax=plt.gca(), fraction=0.046, pad=0.04)
cbar.set_ticks([0, 0.2, 0.4, 0.6, 0.8, 1])
cbar.set_ticklabels(['0', '5', '10', '15', '20', '25'])

plt.tight_layout()
plt.show()