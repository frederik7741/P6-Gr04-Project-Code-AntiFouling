import cv2
import matplotlib
import numpy as np
import json
import matplotlib.pyplot as plt
import os
from PIL import Image, ImageDraw
from numpy.lib.stride_tricks import as_strided


def calculate_similarity_with_as_strided(image_uint8, window_size, comparison_threshold):
    H, W = image_uint8.shape
    pad_offset = window_size // 2

    padded_image = np.pad(image_uint8, pad_width=pad_offset, mode='reflect')
    
    sH, sW = padded_image.strides
    strided_windows_view = as_strided(
        padded_image,
        shape=(H, W, window_size, window_size),
        strides=(sH, sW, sH, sW)
    )
    
    center_pixel_values_view = image_uint8[:, :, np.newaxis, np.newaxis]

    strided_windows_float = strided_windows_view.astype(np.float64)
    center_values_float = center_pixel_values_view.astype(np.float64)
    
    is_window_all_zero = np.all(strided_windows_float == 0.0, axis=(2, 3))

    abs_differences = np.abs(strided_windows_float - center_values_float)
    
    similarity_mask = abs_differences <= comparison_threshold
    similarity_counts = np.sum(similarity_mask, axis=(2, 3))
    
    final_counts = np.where(is_window_all_zero, 0, similarity_counts)
    
    return final_counts.astype(np.int32) 


def compute_iou_pixel_count(gt, pt):
    groundT = np.count_nonzero(gt)
    predictedT = np.count_nonzero(pt)
    intersection_pixels = np.count_nonzero(np.logical_and(gt, pt))
    union_pixels = groundT + predictedT - intersection_pixels

    if union_pixels == 0:
        return 0.0  

    return intersection_pixels / union_pixels

def determine_if_fouling(similarity_raw_count, similarity_thresh=5):
    if similarity_thresh <= similarity_raw_count:
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

image_path = "Months/Month 2/AD3_month_2.png"
filename_after_second_slash = "/".join(image_path.split("/", 2)[2:])
json_path = "Labelled Data - Detect Fouling/Labelled Data Month 2 - 90/AD3_month_2.json"
similarity_threshold = 5

image_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
image_color = cv2.imread(image_path, cv2.IMREAD_COLOR) 
image_rgb = cv2.cvtColor(image_color, cv2.COLOR_BGR2RGB)
height, width = image_gray.shape[:2]

with open(json_path, 'r') as f:
    data = json.load(f)
    
panel_mask = Image.new("L", (width, height), 0)
fouling_mask = Image.new("L", (width, height), 0)
none_mask = Image.new("L", (width, height), 0)

draw_panel = ImageDraw.Draw(panel_mask)
draw_fouling = ImageDraw.Draw(fouling_mask)
draw_none = ImageDraw.Draw(none_mask)

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


panel_mask_np = np.array(panel_mask)
fouling_mask_np = np.array(fouling_mask)
none_mask_np = np.array(none_mask)

blur = cv2.GaussianBlur(image_gray, (5, 5), 0) 
sobel_x = cv2.Sobel(image_gray, cv2.CV_64F, 1, 0, ksize=3)
sobel_y = cv2.Sobel(image_gray, cv2.CV_64F, 0, 1, ksize=3)
gradient_magnitude = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
gradient_magnitude = (gradient_magnitude / gradient_magnitude.max()) * 255
gradient_magnitude = gradient_magnitude.astype(np.uint8)

print("Starting similarity count...")
similarity_count = calculate_similarity_with_as_strided(gradient_magnitude, 
                                                window_size=5, 
                                                comparison_threshold=5)
print("Finished similarity count")

panel_boolean_mask = (panel_mask_np == 1)
fouling_mask_filtered = np.logical_and(fouling_mask_np == 1, none_mask_np == 0)

output_mask_fouling = np.zeros_like(gradient_magnitude, dtype=np.uint8)
output_mask_non_fouling = np.zeros_like(gradient_magnitude, dtype=np.uint8)
panel_coords_y, panel_coords_x = np.where(panel_boolean_mask)
    
output_mask = np.zeros_like(gradient_magnitude, dtype=np.uint8)
for k in range(len(panel_coords_y)):
    y = panel_coords_y[k]
    x = panel_coords_x[k]
    raw_similarity = similarity_count[y, x]
    if not determine_if_fouling(raw_similarity, similarity_thresh=similarity_threshold):
        output_mask[y, x] = 255

iou = compute_iou_pixel_count(fouling_mask_filtered, output_mask)
print(f"IoU: {iou:.3f}")


max_similarity_raw_count = 25
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




plt.figure(figsize=(15, 5))
plt.suptitle(f"Panel: {filename_after_second_slash}| Similarity Thresh: {similarity_threshold}| IoU: {iou:.3f}", fontsize=16)  

plt.subplot(1, 4, 1)
im = plt.imshow(normalized_similarity_on_panel, cmap=custom_cmap, vmin=0, vmax=1)
plt.title("Similarity Heatmap")
plt.axis('off')
cbar = plt.colorbar(im, ax=plt.gca(), fraction=0.046, pad=0.04)
cbar.set_ticks([0, 0.2, 0.4, 0.6, 0.8, 1])
cbar.set_ticklabels(['0', '5', '10', '15', '20', '25'])

plt.subplot(1, 4, 2)
plt.imshow(output_mask, cmap='gray')
plt.title("Predicted Fouling Mask")
plt.axis('off')

plt.subplot(1, 4, 3)
plt.imshow(fouling_mask_filtered, cmap='gray')
plt.title("Ground Truth Mask")
plt.axis('off')

plt.subplot(1, 4, 4)
plt.imshow(image_rgb) 
plt.title("Original Color Image")
plt.axis('off')

plt.tight_layout(rect=[0, 0, 1, 0.95]) 
plt.show()
