# Computer Vision for Anti-Fouling Assessment

## Project Overview

**Detect Fouling** is a modular computer vision system designed to automate the assessment of biofouling on anti-fouling coated panels. The project aims to replace the traditional, manual, and subjective inspection process with a more efficient, consistent, and scalable alternative.

Biofouling inspection traditionally involves manual assessments, which are labor-intensive and inconsistent due to human perception variability and environmental factors. This project introduces an automated pipeline to improve accuracy, efficiency, and usability in the evaluation of fouling growth.

### Key Objectives

The system is built around four core modules:

1. **Image Capture**  
   An initial dataset of panel images is collected under diverse conditions.

2. **Panel Isolation**  
   Automatically detects and isolates panels from the image background.

3. **Fouling Detection**  
   Identifies and classifies regions of fouling vs. non-fouling on each panel.

4. **Graphical User Interface (GUI)**  
   Provides an interactive interface for comparing fouling growth across time and panels.

### System Requirements

- **Automatic Panel Identification**  
  Panels must be automatically detected in each image without manual input.

- **Surface Region Classification**  
  The system must differentiate fouled vs. clean surface areas on the panels.

- **Fouling Area Calculation**  
  Calculates and displays the percentage of the panel covered by fouling.

- **Comparative Growth Analysis**  
  Allows users to visually compare fouling progression across panels and months.

---

## Directory Structure

The repository is organized into the following module directories:

- `Module 1 - Data/`  
  Data such as images and annotations structured according to month or location.

- `Module 1 - Data/`  
  Code for automatic panel isolation and background removal script for figures in section 3.3.

- `Module 3 - Detection of Fouling/`  
  Fouling detection algorithms and scripts for figures in section 3.4.

- `Module 4 - Graphical User Interface/`  
  Graphical user interface components for interactive analysis and scripts for figures in section 3.5.

Each module directory contains scripts and tools focused on a specific stage of the fouling assessment pipeline. More detailed documentation can be found inside the respective module folders.

---

## Authors

- Frederik Nielsen  
- Andreas Hasselholt Jørgensen
- Christian Nørkær Petersen
- Oliver Søndermølle Hansen
- Sture Nicolai Jaque
