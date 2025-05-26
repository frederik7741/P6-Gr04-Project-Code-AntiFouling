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

    for shape in data['shapes']:
        label = shape['label'].lower()
        if len(shape['points']) < 3:
            print(f"Skipping shape with < 3 points: {label}")
            continue

        mask = shape_to_mask(image_shape[:2], shape['points'], shape['shape_type'])

        if label == 'panel':
            panel_mask = np.logical_or(panel_mask, mask)

    return panel_mask.astype(np.uint8)


def create_predicted_panel_mask(image, threshold=135):
    red_channel = image[:, :, 2]
    red_thresh = (red_channel > threshold).astype(np.uint8)
    return red_thresh


def compute_iou(pred_mask, gt_mask):
    pred = pred_mask.astype(bool)
    gt = gt_mask.astype(bool)
    intersection = np.logical_and(pred, gt).sum()
    union = np.logical_or(pred, gt).sum()
    return intersection / union if union != 0 else 0


def process_image(image_path, json_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error reading image: {image_path}")
        return None, None, None

    panel_mask = load_labelme_masks(json_path, image.shape)
    predicted_panel_mask = create_predicted_panel_mask(image)

    iou = compute_iou(predicted_panel_mask, panel_mask) if panel_mask.sum() > 0 else None

    if iou is not None:
        print(f"IoU: {iou:.4f}")
    else:
        print("No panel annotation found.")

    return image, panel_mask, predicted_panel_mask


def process_all_images(image_folder, json_folder):
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    iou_list = []

    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        json_filename = os.path.splitext(image_file)[0] + '.json'
        json_path = os.path.join(json_folder, json_filename)

        if os.path.exists(json_path):
            print(f"Processing {image_file} ...")
            image, panel_mask, predicted_panel_mask = process_image(image_path, json_path)
            if image is not None:
                iou_list.append(compute_iou(predicted_panel_mask, panel_mask))

                # Display image, ground truth, and prediction
                #plt.figure(figsize=(12, 6))

                #plt.subplot(1, 3, 1)
                #plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                #plt.title('Original Image')
                #plt.axis('off')

                #plt.subplot(1, 3, 2)
                #plt.imshow(panel_mask, cmap='gray')
                #plt.title('Ground Truth Mask')
                #plt.axis('off')

                #plt.subplot(1, 3, 3)
                #plt.imshow(predicted_panel_mask, cmap='gray')
                #plt.title('Predicted Mask')
                #plt.axis('off')

                #plt.show()

        else:
            print(f"Skipping {image_file}: matching JSON file not found.")

    if iou_list:
        iou_array = np.array(iou_list)
        mean_iou = np.mean(iou_array)
        median_iou = np.median(iou_array)
        std_iou = np.std(iou_array)
        print("value for Month 0")
        print(f"Mean IoU: {mean_iou:.4f}")
        print(f"Median IoU: {median_iou:.4f}")
        print(f"Standard Deviation of IoU: {std_iou:.4f}")
    else:
        print("No valid IoU values calculated.")


# === USAGE ===
if __name__ == '__main__':
    image_folder = '/Users/sturejaque/Documents/GitHub/P6_Anti_Fouling/Eval Images/Month 0' #put dine dirs på pladserne
    json_folder = '/Users/sturejaque/Desktop/EvalM0'
    process_all_images(image_folder, json_folder)
