# ITMS PRO | AI Surveillance & Inference Tool

A high-performance, professional-grade video inference tool designed for Traffic Management Systems (ITMS). Featuring hierarchical deep learning models for vehicle detection, license plate recognition, and OCR, all wrapped in a premium HUD-style interface.

## 🚀 Key Features

- **Hierarchical Inference Pipeline**:
  - **Stage 1**: Vehicle Detection (YOLOv8)
  - **Stage 2**: License Plate Localization (Crop-based)
  - **Stage 3**: OCR Character Recognition
- **Forensic-Level Logging**:
  - **Millisecond Precision**: Logs include exact video timestamps (`HH:MM:SS.mmm`).
  - **Pixel Metadata**: Detailed reporting of Width, Height, and Area for all detections.
  - **Aggregated OCR Summary**: Instant visibility of full plate text before individual character details.
- **Automated Result Export**:
  - **Unique Per-Inference Folders**: Every inference run creates a traceable workspace (`results/video_name/timestamp_uuid/`).
  - **Full HUD Snapshots**: Captures the complete frame with vehicle/plate overlays.
  - **OCR-Labeled Plate Crops**: Individual plate images saved with character bounding boxes and text labels.
- **Asynchronous Performance**: 
  - Zero-lag video scrubbing via background `SeekWorker`.
  - Multi-threaded inference and playback to maintain 60FPS UI responsiveness.
- **Sleek HUD Overlay**: Subtle pixel coordinate display optimized for varied lighting conditions.

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/Naveenkumar-katomaran/ITMS-Inference-Tool.git
cd ITMS-Inference-Tool

# Install dependencies
pip install PyQt6 ultralytics opencv-python torch pyinstaller
```

## 📁 Project Structure

- `core/`: Inference engine, video handling, and workers.
- `ui/`: PyQt6 windows, widgets, and themes.
- `utils/`: Configuration, logging, result saving, and path resolution.
- `models/`: Destination for AI model weights.
- `logs/`: Daily forensic logs organized by video name.
- `results/`: Exported snapshots and plate crops.

## ⚙️ Configuration & Deployment

### Global Settings (`config.json`)
The system uses a dynamic configuration system. You can modify model paths or confidence thresholds either directly in `config.json` or via the **SETTINGS** button in the UI.

### Standalone Distribution
To build a professional, dynamic standalone version of the tool:
```bash
python3 build_dist.py
```
This will create a `dist/` directory containing a compiled executable. The `config.json` and `models/` folder remain external, allowing you to update configuration or swap models without re-compiling.

## 🎮 Controls & Shortcuts

| Action | Shortcut |
| :--- | :--- |
| **Play/Pause** | `Space` |
| **Next Frame** | `E` or `Right Arrow` |
| **Prev Frame** | `W` or `Left Arrow` |
| **Infer Current Frame**| `I` |
| **Toggle Fullscreen**  | `F11` or `F` |
| **Upload Video/Image** | `O` |
| **Clear Overlay**     | `C` |
| **Zoom In/Out**       | `Scroll Wheel` or `+/-` |
| **Reset Zoom**        | `R` |

---
*Developed for Advanced Traffic Intelligence.*
