# TrueWater — Offline Algae Analyzer (Jetson Nano)


This is an offline-first PySide6 GUI that runs a local YOLOv8 model to detect algae in water sample images. It stores results in a local SQLite database.


## Files to place
- `assets/best.pt` — the YOLOv8 weights
- `assets/image.png` — the reference image


## Quick start (recommended)
1. Create virtualenv and activate:


```bash
python3 -m venv env
source env/bin/activate