# import os
# import cv2
# import numpy as np
# import json
# from PIL import Image, ImageDraw
#
# def load_labelme_annotation(path):
#     with open(path, 'r') as f:
#         return json.load(f)
#
#
# def polygons_to_mask(polygons, img_shape):
#     mask = np.zeros(img_shape[:2], dtype=np.uint8)
#     for poly in polygons:
#         pts = np.array(poly, np.int32).reshape((-1, 1, 2))
#         cv2.fillPoly(mask, [pts], 1)
#     return mask
#
#
# def extract_masks(labelme_data):
#     shapes = labelme_data['shapes']
#     fouling_polys = []
#     none_polys = []
#     panel_polys = []
#
#     for shape in shapes:
#         label = shape['label'].lower()
#         points = shape['points']
#         if label == 'fouling':
#             fouling_polys.append(points)
#         elif label == 'none':
#             none_polys.append(points)
#         elif label == 'panel':
#             panel_polys.append(points)
#
#     img_shape = (labelme_data['imageHeight'], labelme_data['imageWidth'], 3)
#
#     fouling_mask = polygons_to_mask(fouling_polys, img_shape)
#     none_mask = polygons_to_mask(none_polys, img_shape)
#     panel_mask = polygons_to_mask(panel_polys, img_shape)
#
#     fouling_final = np.clip(fouling_mask - none_mask, 0, 1)
#     not_fouling = np.clip(panel_mask - fouling_final, 0, 1)
#
#     return fouling_final.astype(bool), not_fouling.astype(bool)
#
#
# def collect_red_channel_values(image, fouling_mask, not_fouling_mask):
#     red_channel = image[:, :, 2]
#     fouling_vals = red_channel[fouling_mask]
#     not_fouling_vals = red_channel[not_fouling_mask]
#     return fouling_vals, not_fouling_vals
#
#
# # husk at skife path
# image_folder = "Opdelt-In-lokation/B-image-90"
# annotation_folder = "Opdelt-In-lokation/B_Labeled_90"
#
# fouling_all = []
# not_fouling_all = []
# error_log = []
#
# for filename in os.listdir(image_folder):
#     if filename.endswith('.png') or filename.endswith('.jpg'):
#         image_path = os.path.join(image_folder, filename)
#         json_name = os.path.splitext(filename)[0] + ".json"
#         json_path = os.path.join(annotation_folder, json_name)
#

#         image_color = cv2.imread(image_path, cv2.IMREAD_COLOR)
#         if image_color is None:
#             print(f"[ERROR] Failed to load image: {filename}")
#             continue
#
#         image = cv2.cvtColor(image_color, cv2.COLOR_BGR2GRAY)
#
#         if not os.path.exists(json_path):
#             print(f"[ERROR] Missing JSON for image: {filename}")
#             continue
#
#         try:
#             label_data = load_labelme_annotation(json_path)
#         except Exception as e:
#             print(f"[ERROR] Could not read JSON {filename}: {e}")
#             error_log.append((filename, "Invalid JSON or unreadable"))
#             continue
#
#         try:
#             fouling_mask, not_fouling_mask = extract_masks(label_data)
#             fouling_vals, not_fouling_vals = collect_red_channel_values(image_color, fouling_mask, not_fouling_mask)
#             fouling_all.extend(fouling_vals)
#             not_fouling_all.extend(not_fouling_vals)
#             print(f"Processed: {filename}")
#         except Exception as e:
#             print(f"[ERROR] Exception during processing {filename}: {e}")
#             error_log.append((filename, str(e)))
#
# # Plot histogram
# bins = np.arange(257)
# fouling_hist, _ = np.histogram(fouling_all, bins=bins, density=True)
# not_fouling_hist, _ = np.histogram(not_fouling_all, bins=bins, density=True)
#
# import matplotlib.pyplot as plt
#
# plt.figure(figsize=(10, 6))
# plt.plot(bins[:-1], fouling_hist, color='red', label='Fouling')
# plt.plot(bins[:-1], not_fouling_hist, 'r:', label='Panel')  # Changed the color to red with dotted line
# plt.xlabel('Red Channel Intensity')
# plt.ylabel('Normalized Frequency')
# plt.title('Red Channel Intensity Distribution')
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()
#
#
# if error_log:
#     print("\n=== SUMMARY OF ERRORS ===")
#     for filename, reason in error_log:
#         print(f"{filename}: {reason}")
# else:
#     print("\nNo errors encountered.")
#
#
#
    #######################################HSV##########################
import os
import cv2
import numpy as np
import json
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

def load_labelme_annotation(path):
    with open(path, 'r') as f:
        return json.load(f)

def polygons_to_mask(polygons, img_shape):
    mask = np.zeros(img_shape[:2], dtype=np.uint8)
    for poly in polygons:
        pts = np.array(poly, np.int32).reshape((-1, 1, 2))
        cv2.fillPoly(mask, [pts], 1)
    return mask

def extract_masks(labelme_data):
    shapes = labelme_data['shapes']
    fouling_polys = []
    none_polys = []
    panel_polys = []

    for shape in shapes:
        label = shape['label'].lower()
        points = shape['points']
        if label == 'fouling':
            fouling_polys.append(points)
        elif label == 'none':
            none_polys.append(points)
        elif label == 'panel':
            panel_polys.append(points)

    img_shape = (labelme_data['imageHeight'], labelme_data['imageWidth'], 3)

    fouling_mask = polygons_to_mask(fouling_polys, img_shape)
    none_mask = polygons_to_mask(none_polys, img_shape)
    panel_mask = polygons_to_mask(panel_polys, img_shape)

    fouling_final = np.clip(fouling_mask - none_mask, 0, 1)
    not_fouling = np.clip(panel_mask - fouling_final, 0, 1)

    return fouling_final.astype(bool), not_fouling.astype(bool)

def collect_hue_values(image, fouling_mask, not_fouling_mask):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hue_channel = hsv_image[:, :, 0]
    fouling_vals = hue_channel[fouling_mask]
    not_fouling_vals = hue_channel[not_fouling_mask]
    return fouling_vals, not_fouling_vals

image_folder = "Opdelt-In-lokation/K-image-90"
annotation_folder = "Opdelt-In-lokation/K_Labeled_90"

fouling_all = []
not_fouling_all = []
error_log = []

for filename in os.listdir(image_folder):
    if filename.endswith('.png') or filename.endswith('.jpg'):
        image_path = os.path.join(image_folder, filename)
        json_name = os.path.splitext(filename)[0] + ".json"
        json_path = os.path.join(annotation_folder, json_name)

        image_color = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if image_color is None:
            print(f"[ERROR] Failed to load image: {filename}")
            continue

        if not os.path.exists(json_path):
            print(f"[ERROR] Missing JSON for image: {filename}")
            continue

        try:
            label_data = load_labelme_annotation(json_path)
        except Exception as e:
            print(f"[ERROR] Could not read JSON {filename}: {e}")
            error_log.append((filename, "Invalid JSON or unreadable"))
            continue

        try:
            fouling_mask, not_fouling_mask = extract_masks(label_data)
            fouling_vals, not_fouling_vals = collect_hue_values(image_color, fouling_mask, not_fouling_mask)
            fouling_all.extend(fouling_vals)
            not_fouling_all.extend(not_fouling_vals)
            print(f"Processed: {filename}")
        except Exception as e:
            print(f"[ERROR] Exception during processing {filename}: {e}")
            error_log.append((filename, str(e)))

bins = np.arange(181)  
fouling_hist, _ = np.histogram(fouling_all, bins=bins, density=True)
not_fouling_hist, _ = np.histogram(not_fouling_all, bins=bins, density=True)

plt.figure(figsize=(10, 6))
plt.plot(bins[:-1], fouling_hist, color='red', label='Fouling')   
plt.plot(bins[:-1], not_fouling_hist, 'r:', label='Panel')       
plt.xlabel('Hue Value (0–179)')
plt.ylabel('Normalized Frequency')
plt.title('Hue Distribution in HSV Color Space')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


if error_log:
    print("\n=== SUMMARY OF ERRORS ===")
    for filename, reason in error_log:
        print(f"{filename}: {reason}")
else:
    print("\nNo errors encountered.")
