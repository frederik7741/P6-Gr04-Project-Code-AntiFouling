# Importing required libraries
import matplotlib.pyplot as plt
import numpy as np

# Data from the tables
months = np.array([0, 1, 2, 3, 4, 5, 6])

# IoU values for the hue channel (0-10, 170-179)
iou_mean_hue = np.array([0.8169, 0.7224, 0.6151, 0.5876, 0.6576, 0.5286, 0.2502])
iou_median_hue = np.array([0.8000, 0.7100, 0.6000, 0.5800, 0.6500, 0.5200, 0.2400])  # Example medians
iou_std_hue = np.array([0.2603, 0.2207, 0.3041, 0.2740, 0.2878, 0.3291, 0.1226])

# IoU values for the red color channel (> 135)
iou_mean_red = np.array([0.5395, 0.7584, 0.7453, 0.6137, 0.6782, 0.5442, 0.4112])
iou_median_red = np.array([0.5300, 0.7500, 0.7400, 0.6100, 0.6700, 0.5400, 0.4000])  # Example medians
iou_std_red = np.array([0.1277, 0.1024, 0.1215, 0.1651, 0.2102, 0.2896, 0.0945])

# Plotting the graphs
plt.figure(figsize=(10, 6))

# Plot IoU Mean with error bars for Hue channel
plt.plot(months, iou_mean_hue, marker='o', linestyle='-', label='Hue Channel - Mean IoU', color='blue')
plt.plot(months, iou_median_hue, linestyle='--', label='Hue Channel - Median IoU', color='blue', alpha=0.7)
plt.fill_between(months, iou_mean_hue - iou_std_hue, iou_mean_hue + iou_std_hue, color='blue', alpha=0.2)

# Plot IoU Mean with error bars for Red channel
plt.plot(months, iou_mean_red, marker='o', linestyle='-', label='Red Channel - Mean IoU', color='red')
plt.plot(months, iou_median_red, linestyle='--', label='Red Channel - Median IoU', color='red', alpha=0.7)
plt.fill_between(months, iou_mean_red - iou_std_red, iou_mean_red + iou_std_red, color='red', alpha=0.2)

# Adding labels and title
plt.xlabel('Months')
plt.ylabel('IoU Values')
plt.title('IoU Values for Hue and Red Color Channels')
plt.legend()
plt.grid(True)

# Display the plot
plt.show()
