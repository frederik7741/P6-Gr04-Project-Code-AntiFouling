import re
import cv2
import numpy as np
import json
import matplotlib.pyplot as plt
import os
from PIL import Image, ImageDraw
from scipy.ndimage import generic_filter
import csv
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
        return 0.0  # ungå at division med 0

    return intersection_pixels / union_pixels

def determine_if_fouling(similarity_raw_count, similarity_thresh):
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

def get_month_from_filename(fname):
    """
    Extracts the month number from a filename expected to contain '_month_Y'.
    Example: 'someprefix_month_3.png' -> 3
    """
    match = re.search(r'_month_(\d+)', fname, re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            print(f"[!] Warning: Could not parse month number from '{match.group(1)}' in filename '{fname}'")
            return None
    return None

image_folder = "C:/Users/ChristianPetersen/Desktop/Combined Images"
json_folder = "C:/Users/ChristianPetersen/Desktop/Combined Jsons"

output_folder = "generated_data_everything"

j_threshold_values = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

csv_filename = os.path.join(output_folder, "fouling_iou_results.csv")
csv_headers = ["Filename","IoU_1","IoU_2","IoU_3","IoU_4", "IoU_5","IoU_6","IoU_7","IoU_8","IoU_9", "IoU_10","IoU_11","IoU_12","IoU_13","IoU_14", "IoU_15","IoU_16","IoU_17","IoU_18","IoU_19", "IoU_20","IoU_21","IoU_22","IoU_23","IoU_24","IoU_25", "Best_IoU_Thresh", "Best_IoU_Value"]

with open(csv_filename, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(csv_headers)
    
    for filename in os.listdir(image_folder):
        if not (filename.endswith(".png") or filename.endswith(".jpg")):
            continue

        image_path = os.path.join(image_folder, filename)
        json_name = os.path.splitext(filename)[0] + ".json"
        json_path = os.path.join(json_folder, json_name)

        month = get_month_from_filename(filename)
        is_target_month = month is not None and 1 <= month <= 6

        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None or not os.path.exists(json_path):
            print(f"[!] Skipped {filename}: missing image or JSON")
            continue

        height, width = image.shape
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
            else:
                print(f"[!] Skipping shape in {filename} with label '{label}' due to insufficient points.")

        panel_mask_np = np.array(panel_mask)
        fouling_mask_np = np.array(fouling_mask)
        none_mask_np = np.array(none_mask)

        # --- Gradient & Similarity ---
        sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
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
        
        iou_scores_for_file = {}
        
        for i, j_thresh in enumerate(j_threshold_values):
            current_output_mask = np.zeros_like(gradient_magnitude, dtype=np.uint8)
            print(f"Processing {filename} with j_thresh = {j_thresh}")
            for k in range(len(panel_coords_y)):
                y = panel_coords_y[k]
                x = panel_coords_x[k]
                raw_similarity = similarity_count[y, x]
                if not determine_if_fouling(raw_similarity, j_thresh):
                    current_output_mask[y, x] = 255
                    
            current_iou = compute_iou_pixel_count(fouling_mask_filtered, current_output_mask)
            iou_scores_for_file[j_thresh] = round(current_iou, 4)
            print(f"IOU for {j_thresh}: {current_iou:.4f}")
            
        best_iou_value = -1.0
        best_iou_thresh = None
        
        if iou_scores_for_file: 
            for j_val, iou_val in iou_scores_for_file.items():
                if iou_val > best_iou_value:
                    best_iou_value = iou_val
                    best_iou_thresh = j_val
        row_data = [
            filename,
            iou_scores_for_file.get(1, 'N/A'), 
            iou_scores_for_file.get(2, 'N/A'), 
            iou_scores_for_file.get(3, 'N/A'), 
            iou_scores_for_file.get(4, 'N/A'), 
            iou_scores_for_file.get(5, 'N/A'),
            iou_scores_for_file.get(6, 'N/A'), 
            iou_scores_for_file.get(7, 'N/A'), 
            iou_scores_for_file.get(8, 'N/A'), 
            iou_scores_for_file.get(9, 'N/A'), 
            iou_scores_for_file.get(10, 'N/A'),
            iou_scores_for_file.get(11, 'N/A'),
            iou_scores_for_file.get(12, 'N/A'),
            iou_scores_for_file.get(13, 'N/A'),
            iou_scores_for_file.get(14, 'N/A'),
            iou_scores_for_file.get(15, 'N/A'),
            iou_scores_for_file.get(16, 'N/A'),
            iou_scores_for_file.get(17, 'N/A'),
            iou_scores_for_file.get(18, 'N/A'),
            iou_scores_for_file.get(19, 'N/A'),
            iou_scores_for_file.get(20, 'N/A'),
            iou_scores_for_file.get(21, 'N/A'),
            iou_scores_for_file.get(22, 'N/A'),
            iou_scores_for_file.get(23, 'N/A'),
            iou_scores_for_file.get(24, 'N/A'),
            iou_scores_for_file.get(25, 'N/A'),
            
            best_iou_thresh if best_iou_thresh is not None else 'N/A',
            f"{best_iou_value:.4f}" if best_iou_value != -1.0 else 'N/A'
        ]
        csv_writer.writerow(row_data)
        print(f"Finished processing {filename}. Results saved for CSV.")
