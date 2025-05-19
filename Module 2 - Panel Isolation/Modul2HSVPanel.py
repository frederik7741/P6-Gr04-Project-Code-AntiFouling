import json
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os

def extract_hsv_pixels(image, annotation, outside=False):
    # Create a mask of the 'panel' area
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    points = np.array(annotation['points'], dtype=np.int32)
    cv2.fillPoly(mask, [points], 255)

    if outside:
        mask = cv2.bitwise_not(mask)

    # Convert to HSV and extract channels
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hue, saturation, value = cv2.split(hsv_image)

    # Apply the mask (inside or outside the panel)
    hue_pixels = hue[mask == 255]
    saturation_pixels = saturation[mask == 255]
    value_pixels = value[mask == 255]

    return hue_pixels, saturation_pixels, value_pixels


def process_json_files(json_folder):
    all_inside_hue = []
    all_inside_saturation = []
    all_inside_value = []
    all_outside_hue = []
    all_outside_saturation = []
    all_outside_value = []

    # List all json files in the folder
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]

    for json_file in json_files:
        json_path = os.path.join(json_folder, json_file)

        with open(json_path) as f:
            data = json.load(f)

        image_path = data.get('imagePath')

        if not image_path or not os.path.exists(image_path):
            print(f"Warning: Image path {image_path} not found. Skipping this file.")
            continue

        image = cv2.imread(image_path)

        if image is None:
            print(f"Warning: Could not open image {image_path}. Skipping this file.")
            continue

        for annotation in data['shapes']:
            if annotation['label'] == 'panel':
                inside_hue, inside_saturation, inside_value = extract_hsv_pixels(image, annotation, outside=False)
                outside_hue, outside_saturation, outside_value = extract_hsv_pixels(image, annotation, outside=True)

                all_inside_hue.extend(inside_hue)
                all_inside_saturation.extend(inside_saturation)
                all_inside_value.extend(inside_value)

                all_outside_hue.extend(outside_hue)
                all_outside_saturation.extend(outside_saturation)
                all_outside_value.extend(outside_value)

    return (np.array(all_inside_hue), np.array(all_inside_saturation), np.array(all_inside_value),
            np.array(all_outside_hue), np.array(all_outside_saturation), np.array(all_outside_value))


def plot_hsv_histograms(inside, outside, title):
    hist_inside, bins_inside = np.histogram(inside, bins=50, range=(0, 256), density=True)
    hist_outside, bins_outside = np.histogram(outside, bins=50, range=(0, 256), density=True)
    bin_centers_inside = (bins_inside[:-1] + bins_inside[1:]) / 2
    bin_centers_outside = (bins_outside[:-1] + bins_outside[1:]) / 2

    plt.figure(figsize=(10, 6))
    plt.plot(bin_centers_inside, hist_inside, color='blue', label='Inside Panel', linewidth=2)
    plt.plot(bin_centers_outside, hist_outside, color='orange', linestyle='--', label='Outside Panel', linewidth=2)
    plt.title(f'{title} Distribution Inside vs Outside the Panel')
    plt.xlabel(f'{title} Intensity')
    plt.ylabel('Normalized Frequency')
    plt.legend()
    plt.grid(False)
    plt.show()


json_folder = '/Users/sturejaque/Desktop/m0'  # Replace with actual folder path
inside_hue, inside_saturation, inside_value, outside_hue, outside_saturation, outside_value = process_json_files(json_folder)

plot_hsv_histograms(inside_hue, outside_hue, 'Hue')
plot_hsv_histograms(inside_saturation, outside_saturation, 'Saturation')
plot_hsv_histograms(inside_value, outside_value, 'Value')
