import json
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os

def extract_red_pixels(image, annotation, outside=False):
    # Create a mask of the 'panel' area
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    points = np.array(annotation['points'], dtype=np.int32)
    cv2.fillPoly(mask, [points], 255)

    if outside:
        mask = cv2.bitwise_not(mask)

    # Extract the red channel
    red_channel = image[:, :, 2]

    # Apply the mask (inside or outside the panel)
    red_pixels = red_channel[mask == 255]

    return red_pixels

def process_json_files(json_folder):
    all_inside_red = []
    all_outside_red = []

    # List all json files in the folder
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]

    for json_file in json_files:
        json_path = os.path.join(json_folder, json_file)

        with open(json_path) as f:
            data = json.load(f)

        # Extract the image path from the JSON file (assuming it's in the 'imagePath' field)
        image_path = data.get('imagePath')

        if not image_path or not os.path.exists(image_path):
            print(f"Warning: Image path {image_path} not found. Skipping this file.")
            continue  # Skip this file and proceed to the next one

        # Load the corresponding image
        image = cv2.imread(image_path)

        if image is None:
            print(f"Warning: Could not open image {image_path}. Skipping this file.")
            continue  # Skip this file and proceed to the next one

        # Loop through each annotation
        for annotation in data['shapes']:
            if annotation['label'] == 'panel':  # Check if the annotation is for the 'panel'
                # Get red pixels inside the panel area
                inside_red = extract_red_pixels(image, annotation, outside=False)
                all_inside_red.extend(inside_red)

                # Get red pixels outside the panel area
                outside_red = extract_red_pixels(image, annotation, outside=True)
                all_outside_red.extend(outside_red)

    return np.array(all_inside_red), np.array(all_outside_red)

def plot_combined_red_histogram(inside_red, outside_red):
    # Initialize histograms for red channel (inside and outside the panel)
    hist_inside, bins_inside = np.histogram(inside_red, bins=50, range=(0, 256), density=True)
    hist_outside, bins_outside = np.histogram(outside_red, bins=50, range=(0, 256), density=True)

    # Get the bin centers for both histograms
    bin_centers_inside = (bins_inside[:-1] + bins_inside[1:]) / 2
    bin_centers_outside = (bins_outside[:-1] + bins_outside[1:]) / 2

    # Plot the combined red histogram without fills
    plt.figure(figsize=(10, 6))
    plt.plot(bin_centers_inside, hist_inside, color='r', label='Inside Panel', linewidth=2)
    plt.plot(bin_centers_outside, hist_outside, color='r', linestyle='--', label='Outside Panel', linewidth=2)

    # Labels and title
    plt.title('Red Pixel Distribution Inside vs Outside the Panel')
    plt.xlabel('Red Pixel Intensity')
    plt.ylabel('Normalized Frequency')
    plt.legend()
    plt.grid(False)
    plt.show()

# Path to the folder containing the JSON files
json_folder = '/Users/sturejaque/Desktop/m0'  # Replace with the actual folder path

# Process the files and get the red pixel data
inside_red, outside_red = process_json_files(json_folder)

# Plot the combined red histogram
plot_combined_red_histogram(inside_red, outside_red)
