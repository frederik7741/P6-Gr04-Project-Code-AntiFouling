# P6 Anti-Fouling: Image Analysis and Segmentation Tools

This module aims to accurately and automatically isolate the panel, distinguishing it from
the background. However, due to the unpredictable nature of fouling and the evolving
appearance of the panels over time, isolating the panel required a multifaceted approach. Therefore, this module contains
script used for isolating the panel and evaluating the isolation.
---

##  Modules Overview

### 1. `Modul2Plot.py` —  _Performance Visualization_

Plots **IoU scores over time** comparing two thresholding techniques:

- **Red channel thresholding** (`Red > 135`)
- **Hue-based thresholding** (`Hue in [0–10] ∪ [170–179]`)

**Features:**
- Displays mean and median IoUs per month
- Includes standard deviation error bands

---

### 2. `Modul2RGBALL.py` —  _Combined RGB Histogram_

Analyzes all images in a folder and plots the **combined, normalized RGB histograms**.

**Features:**
- Aggregates red, green, and blue channel histograms across all images
- Normalized by the total number of pixels

**Usage:**
- Set `folder_path` to your dataset folder (e.g., images from one month)

---

### 3. `Modul2RGBPanel.py` —  _Panel vs Background Red Histogram_

Analyzes red channel intensity **inside vs outside** the annotated "panel" region.

**Features:**
- Reads `LabelMe` JSON annotations
- Extracts red pixel values from:
  - Inside panel area
  - Outside panel area
- Plots overlaid histograms for comparison

**Purpose:**
- Determine if red-channel intensity alone can separate fouled panels from background

---

### 4. `Modul2Threshold135.py` — _Red Channel Thresholding (135)_

Applies a **simple threshold (135) on the red channel** to detect panels and compares against LabelMe masks.

**Features:**
- Generates binary mask using `Red > 135`
- Computes IoU with annotated panel masks
- Outputs:
  - Mean IoU
  - Median IoU
  - Standard deviation of IoUs

**Use case:**  
Quick evaluation of red thresholding as a segmentation method.

---

### 5. `Modul2ThresholdHSV.py` —  _Hue-Based Thresholding_

Segments red-hued areas using the **HSV color space**.

**Features:**
- Converts BGR → HSV
- Creates binary mask for hue ranges `[0–10]` and `[170–179]`
- Compares with ground-truth annotations via IoU

---

### 6. `Modul2HSVhistogram.py` — _Hue Histogram for Panel vs Background_

Compares the **distribution of hue values** inside and outside the panel.

**Features:**
- Extracts hue values using LabelMe JSONs
- Plots histograms of hue intensities
  - Inside panel vs outside panel
- Helps visually confirm whether hue-based segmentation is effective

---

## Authors

- Frederik Nielsen  
- Andreas Hasselholt Jørgensen
- Christian Nørkær Petersen
- Oliver Søndermølle Hansen
- Sture Nicolai Jaque

