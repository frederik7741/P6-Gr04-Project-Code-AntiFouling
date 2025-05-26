# import json
# import numpy as np
# import cv2
# import matplotlib.pyplot as plt
# import os
# from labelme.utils import shape_to_mask
#
#
# def load_labelme_masks(json_path, image_shape):
#     with open(json_path, 'r') as f:
#         data = json.load(f)
#
#     panel_mask = np.zeros(image_shape[:2], dtype=np.uint8)
#     fouling_mask_annotated = np.zeros(image_shape[:2], dtype=np.uint8)
#     none_mask = np.zeros(image_shape[:2], dtype=np.uint8)
#     panel_shapes = []
#
#     for shape in data['shapes']:
#         label = shape['label'].lower()
#         if len(shape['points']) < 3:
#             print(f" Skipping shape with < 3 points: {label}")
#             continue
#
#         mask = shape_to_mask(image_shape[:2], shape['points'], shape['shape_type'])
#
#         if label == 'panel':
#             panel_mask = np.logical_or(panel_mask, mask)
#             panel_shapes.append(shape)
#         elif label == 'fouling':
#             fouling_mask_annotated = np.logical_or(fouling_mask_annotated, mask)
#         elif label == 'none':
#             none_mask = np.logical_or(none_mask, mask)
#
#     fouling_mask_annotated = np.logical_and(fouling_mask_annotated, np.logical_not(none_mask))
#
#     return panel_mask.astype(np.uint8), fouling_mask_annotated.astype(np.uint8), panel_shapes
#
#
# def create_predicted_masks(image, panel_mask, threshold=175):
#     red_channel = image[:, :, 2]
#     red_thresh = (red_channel > threshold).astype(np.uint8)
#     panel_red_mask = np.logical_and(red_thresh, panel_mask).astype(np.uint8)
#     fouling_mask = np.logical_and(np.logical_not(red_thresh), panel_mask).astype(np.uint8)
#     return panel_red_mask, fouling_mask
#
#
# def draw_panel_contours(base_image, panel_shapes, color=(0, 255, 0)):
#     img = base_image.copy()
#     for shape in panel_shapes:
#         points = np.array(shape['points'], dtype=np.int32)
#         points = points.reshape((-1, 1, 2))
#         cv2.polylines(img, [points], isClosed=True, color=color, thickness=2)
#     return img
#
#
# def compute_iou(pred_mask, gt_mask):
#     pred = pred_mask.astype(bool)
#     gt = gt_mask.astype(bool)
#     intersection = np.logical_and(pred, gt).sum()
#     union = np.logical_or(pred, gt).sum()
#     return intersection / union if union != 0 else 0
#
#
# def visualize_all(image, panel_red_mask, fouling_mask_predicted, fouling_mask_annotated,
#                   panel_mask, panel_shapes, iou=None, filename=None):
#     overlaid_image = draw_panel_contours(image, panel_shapes)
#     img_with_text = overlaid_image.copy()
#
#     if iou is not None:
#         cv2.putText(img_with_text, f"IoU: {iou:.4f}", (10, 30),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#
#     plt.figure(figsize=(20, 10))
#
#     plt.subplot(2, 3, 1)
#     plt.imshow(cv2.cvtColor(img_with_text, cv2.COLOR_BGR2RGB))
#     plt.title('Original Image + Panel (IoU on image)')
#     plt.axis('off')
#
#     plt.subplot(2, 3, 2)
#     plt.imshow(panel_red_mask, cmap='gray')
#     plt.title("Panel Mask (Red > 175)")
#     plt.axis('off')
#
#     plt.subplot(2, 3, 3)
#     plt.imshow(fouling_mask_predicted, cmap='gray')
#     plt.title(f"Predicted Fouling Mask IoU: {iou:.4f}" if iou else "Predicted Fouling Mask")
#     plt.axis('off')
#
#     plt.subplot(2, 3, 4)
#     plt.imshow(fouling_mask_annotated, cmap='gray')
#     plt.title('Annotated Fouling Mask')
#     plt.axis('off')
#
#     plt.subplot(2, 3, 5)
#     plt.imshow(panel_mask, cmap='gray')
#     plt.title('Panel Area Mask')
#     plt.axis('off')
#
#     if filename:
#         plt.suptitle(f"Results for: {filename}", fontsize=18)
#
#     plt.tight_layout(rect=[0, 0, 1, 0.95])
#     plt.show()
#
#
# def process_image(image_path, json_path):
#     image = cv2.imread(image_path)
#     if image is None:
#         print(f"Error reading image: {image_path}")
#         return
#
#     filename = os.path.basename(image_path)
#     panel_mask, fouling_mask_annotated, panel_shapes = load_labelme_masks(json_path, image.shape)
#     panel_red_mask, fouling_mask_predicted = create_predicted_masks(image, panel_mask)
#     iou = compute_iou(fouling_mask_predicted, fouling_mask_annotated) if fouling_mask_annotated.sum() > 0 else None
#
#     #visualize_all(image, panel_red_mask, fouling_mask_predicted,
#                  # fouling_mask_annotated, panel_mask, panel_shapes, iou, filename)
#
#     if iou is not None:
#         print(f"IoU with annotated fouling: {iou:.4f}")
#     else:
#         print(f"{filename}: No annotated fouling found in JSON.")
#
#
# def process_all_images(image_folder, json_folder):
#     image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
#
#     for image_file in image_files:
#         image_path = os.path.join(image_folder, image_file)
#         json_filename = os.path.splitext(image_file)[0] + '.json'
#         json_path = os.path.join(json_folder, json_filename)
#
#         if os.path.exists(json_path):
#             print(f"Processing {image_file} ...")
#             process_image(image_path, json_path)
#         else:
#             print(f"Skipping {image_file}: matching JSON file not found.")
#
#
# # === USAGE ===
# if __name__ == '__main__':
#     image_folder = 'Opdelt-In-lokation/A-image-90'
#     json_folder = 'Opdelt-In-lokation/A_Labeled_90'
#     process_all_images(image_folder, json_folder)

########################HSV##################################
import json
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
from labelme.utils import shape_to_mask


def load_labelme_masks(json_path, image_shape):
    with open(json_path, 'r') as f:
        data = json.load(f)

    panel_mask = np.zeros(image_shape[:2], dtype=np.uint8)
    fouling_mask_annotated = np.zeros(image_shape[:2], dtype=np.uint8)
    none_mask = np.zeros(image_shape[:2], dtype=np.uint8)
    panel_shapes = []

    for shape in data['shapes']:
        label = shape['label'].lower()
        if len(shape['points']) < 3:
            print(f" Skipping shape with < 3 points: {label}")
            continue

        mask = shape_to_mask(image_shape[:2], shape['points'], shape['shape_type'])

        if label == 'panel':
            panel_mask = np.logical_or(panel_mask, mask)
            panel_shapes.append(shape)
        elif label == 'fouling':
            fouling_mask_annotated = np.logical_or(fouling_mask_annotated, mask)
        elif label == 'none':
            none_mask = np.logical_or(none_mask, mask)

    fouling_mask_annotated = np.logical_and(fouling_mask_annotated, np.logical_not(none_mask))

    return panel_mask.astype(np.uint8), fouling_mask_annotated.astype(np.uint8), panel_shapes


def create_predicted_masks(image, panel_mask):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]

    # Red hue range (in OpenCV, Hue is 0-179)
    mask1 = cv2.inRange(hue, 0, 15)
    mask2 = cv2.inRange(hue, 170, 179)
    red_mask = cv2.bitwise_or(mask1, mask2)
    red_mask_binary = (red_mask > 0).astype(np.uint8)

    panel_red_mask = np.logical_and(red_mask_binary, panel_mask).astype(np.uint8)
    fouling_mask = np.logical_and(np.logical_not(red_mask_binary), panel_mask).astype(np.uint8)
    return panel_red_mask, fouling_mask


def draw_panel_contours(base_image, panel_shapes, color=(0, 255, 0)):
    img = base_image.copy()
    for shape in panel_shapes:
        points = np.array(shape['points'], dtype=np.int32)
        points = points.reshape((-1, 1, 2))
        cv2.polylines(img, [points], isClosed=True, color=color, thickness=2)
    return img


def compute_iou(pred_mask, gt_mask):
    pred = pred_mask.astype(bool)
    gt = gt_mask.astype(bool)
    intersection = np.logical_and(pred, gt).sum()
    union = np.logical_or(pred, gt).sum()
    return intersection / union if union != 0 else 0


def visualize_all(image, panel_red_mask, fouling_mask_predicted, fouling_mask_annotated,
                  panel_mask, panel_shapes, iou=None, filename=None):
    overlaid_image = draw_panel_contours(image, panel_shapes)
    img_with_text = overlaid_image.copy()

    if iou is not None:
        cv2.putText(img_with_text, f"IoU: {iou:.4f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    plt.figure(figsize=(20, 10))

    plt.subplot(2, 3, 1)
    plt.imshow(cv2.cvtColor(img_with_text, cv2.COLOR_BGR2RGB))
    plt.title('Original Image + Panel (IoU on image)')
    plt.axis('off')

    plt.subplot(2, 3, 2)
    plt.imshow(panel_red_mask, cmap='gray')
    plt.title("Panel Mask (Hue in 0–15, 170–179)")
    plt.axis('off')

    plt.subplot(2, 3, 3)
    plt.imshow(fouling_mask_predicted, cmap='gray')
    plt.title(f"Predicted Fouling Mask IoU: {iou:.4f}" if iou else "Predicted Fouling Mask")
    plt.axis('off')

    plt.subplot(2, 3, 4)
    plt.imshow(fouling_mask_annotated, cmap='gray')
    plt.title('Annotated Fouling Mask')
    plt.axis('off')

    plt.subplot(2, 3, 5)
    plt.imshow(panel_mask, cmap='gray')
    plt.title('Panel Area Mask')
    plt.axis('off')

    if filename:
        plt.suptitle(f"Results for: {filename}", fontsize=18)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()


def process_image(image_path, json_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error reading image: {image_path}")
        return

    filename = os.path.basename(image_path)
    panel_mask, fouling_mask_annotated, panel_shapes = load_labelme_masks(json_path, image.shape)
    panel_red_mask, fouling_mask_predicted = create_predicted_masks(image, panel_mask)
    iou = compute_iou(fouling_mask_predicted, fouling_mask_annotated) if fouling_mask_annotated.sum() > 0 else None

   # visualize_all(image, panel_red_mask, fouling_mask_predicted,
                  #fouling_mask_annotated, panel_mask, panel_shapes, iou, filename)

    if iou is not None:
        print(f"IoU with annotated fouling: {iou:.4f}")
    else:
        print(f"{filename}: No annotated fouling found in JSON.")


def process_all_images(image_folder, json_folder):
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        json_filename = os.path.splitext(image_file)[0] + '.json'
        json_path = os.path.join(json_folder, json_filename)

        if os.path.exists(json_path):
            print(f"Processing {image_file} ...")
            process_image(image_path, json_path)
        else:
            print(f"Skipping {image_file}: matching JSON file not found.")

if __name__ == '__main__':
    image_folder = 'Opdelt-In-lokation/K-image-90'
    json_folder = 'Opdelt-In-lokation/K_Labeled_90'
    process_all_images(image_folder, json_folder)


