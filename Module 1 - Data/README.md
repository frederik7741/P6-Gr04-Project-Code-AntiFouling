# Module 1 - Data

## Overview

**Module 1** serves as the foundation of the fouling detection pipeline. It contains all the raw and annotated image data needed to train and evaluate the system. The images are structured by **time (month)**, with further division into subsets representing **10% and 90%** of the available data.

This module does not contain code, only data, and is designed to be used by the subsequent modules in the pipeline.

---

## Data Structure

### 1. `Months Annotations/`

This directory contains **annotated image data**, grouped by month and further split into **10% and 90% subsets**. These subsets are used for balancing or staging data during model training and evaluation.

Each folder name follows the format:  
`Labelled Data Month X - Y`, where:
- **X** = the month number (0–6)
- **Y** = the subset size (10 for 10%, 90 for 90%)

Some folders may include project-related directories such as `.idea/` and `runs/labelme2coco/`, which are used for managing annotation tool configurations and COCO format conversion.




## Purpose

This module is designed to:

- Store and organize all raw and labeled image data.
- Enable month-based analysis for tracking fouling progression over time.
- Provide 10% and 90% data splits for flexible experimentation and model evaluation.
- Feed consistent input into Module 2 (Panel Isolation), Module 3 (Fouling Detection), and Module 4 (GUI).

---


## Authors

- Frederik Nielsen  
- Andreas Hasselholt Jørgensen
- Christian Nørkær Petersen
- Oliver Søndermølle Hansen
- Sture Nicolai Jaque
