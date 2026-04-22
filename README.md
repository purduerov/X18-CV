# ROV Computer Vision

This repository contains all computer vision related code and resources for the ROV.

---

## File Structure

### `src/`
Contains all core computer vision modules and active development code for the current year's tasks.  
This is where the main logic for detection, processing, and models lives.

### `scripts/`
Lightweight wrapper scripts used to run or test functionality from `src`.  
These should not contain core logic, only execution and orchestration.

### `archive/`
Stores deprecated or experimental code from previous tasks and iterations for reference.

### `data/`
Contains datasets used by the CV pipeline, including:
- Images and video frames
- 3D models
- Other raw or processed data

### `configs/`
Stores configurable parameters for the system (e.g., confidence thresholds, image sizes, model settings).  
*Currently not fully implemented.*

### `docs/`
Documentation explaining how to run, test, and understand each subsystem.

---

## Notes
- Keep `src/` clean and modular.
- Avoid placing logic inside `scripts/`.
- Move unused code to `archive/` instead of deleting it.

---
