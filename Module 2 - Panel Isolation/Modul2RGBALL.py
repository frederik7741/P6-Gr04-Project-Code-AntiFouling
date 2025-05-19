import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

def plot_combined_rgb_histogram(folder_path):
    # Initialize combined histograms for R, G, B channels
    hist_r = np.zeros(256)
    hist_g = np.zeros(256)
    hist_b = np.zeros(256)
    total_pixels = 0

    # Iterate through the folder and process each image
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            image_path = os.path.join(folder_path, filename)
            image = cv2.imread(image_path)

            if image is None:
                print(f"Warning: Failed to load {filename}")
                continue

            # Split the image into R, G, B channels
            b, g, r = cv2.split(image)

            # Calculate histograms and update the combined histograms
            hist_r += cv2.calcHist([r], [0], None, [256], [0, 256]).flatten()
            hist_g += cv2.calcHist([g], [0], None, [256], [0, 256]).flatten()
            hist_b += cv2.calcHist([b], [0], None, [256], [0, 256]).flatten()
            total_pixels += r.size

    # Normalize histograms
    hist_r /= total_pixels
    hist_g /= total_pixels
    hist_b /= total_pixels

    # Plot combined histogram
    plt.figure(figsize=(8, 6))
    plt.plot(hist_r, color='red', label='Red')
    plt.plot(hist_g, color='green', label='Green')
    plt.plot(hist_b, color='blue', label='Blue')
    plt.title('Combined RGB Histogram')
    plt.xlabel('Pixel Intensity')
    plt.ylabel('Normalized Frequency')
    plt.legend()
    plt.show()


folder_path = "/Users/sturejaque/Documents/GitHub/P6_Anti_Fouling/Months/Month 0"
plot_combined_rgb_histogram(folder_path)

