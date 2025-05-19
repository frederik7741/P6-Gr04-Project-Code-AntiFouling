# Module 1 - Data

## Overview

**Module 1** serves as the foundation of the fouling detection pipeline. It contains all the raw and annotated image data needed to train and evaluate the system. The images are structured by **time (month)** and **location**, with further division into subsets representing **10% and 90%** of the available data.

This module does not contain code, only data, and is designed to be used by the subsequent modules in the pipeline.

---

## Data Structure

### 1. `Months/`

This directory contains **raw images** grouped by the month they were taken. Each folder (`Month 0` to `Month 6`) represents the fouling condition at a specific time point during the submersion period. there is also a folder Eval Images with the 10% of the images.


---

### 2. `Months Annotations/`

This directory contains **annotated image data**, grouped by month and further split into **10% and 90% subsets**. These subsets are used for balancing or staging data during model training and evaluation.

Each folder name follows the format:  
`Labelled Data Month X - Y`, where:
- **X** = the month number (1–6)
- **Y** = the subset size (10 for 10%, 90 for 90%)

Some folders may include project-related directories such as `.idea/` and `runs/labelme2coco/`, which are used for managing annotation tool configurations and COCO format conversion.


---

### 3. `Opdelt-In-lokation/`

This directory splits the dataset by **sampling location**: `A` (Baltic Asko), `B`(Atlanten Brest), and `K`(Baltic Transitipon Kristineberg). Each location contains both **raw images** and their **annotations**, divided again into **10% and 90% subsets**.

Folder naming format:
- `A-image-10` → 10% raw images from Location A  
- `A_Labeled_90` → 90% labeled data from Location A  
(And so on for Locations B and K)


---

## Purpose

This module is designed to:

- Store and organize all raw and labeled image data.
- Enable month-based analysis for tracking fouling progression over time.
- Enable location-based analysis to evaluate environmental impact on fouling.
- Provide 10% and 90% data splits for flexible experimentation and model evaluation.
- Feed consistent input into Module 2 (Panel Isolation), Module 3 (Fouling Detection), and Module 4 (GUI).

---


## Authors

- Frederik Nielsen  
- Andreas Hasselholt Jørgensensen
- Christian Nørkær Petersen
- Oliver Søndermølle Hansen
- Sture Nicolai Jaque