# ITMS PRO | AI Surveillance & Inference Tool

A high-performance, professional-grade video inference tool designed for Traffic Management Systems (ITMS). Featuring hierarchical deep learning models for vehicle detection, license plate recognition, and OCR, all wrapped in a premium HUD-style interface.

## 🚀 Key Features

- **Hierarchical Inference Pipeline**:
  - **Stage 1**: Vehicle Detection (YOLOv8)
  - **Stage 2**: License Plate Localization (Crop-based)
  - **Stage 3**: OCR Character Recognition
- **Sleek HUD Interface**: High-contrast, dual-layer bounding boxes designed for both day and night highway conditions.
- **Asynchronous Performance**: 
  - Zero-lag video scrubbing via background `SeekWorker`.
  - Multi-threaded inference and playback to maintain 60FPS UI responsiveness.
- **Dynamic Configuration**: Real-time adjustment of model paths and confidence thresholds via a graphical settings menu.
- **Precision Navigation**: Frame-by-frame stepping with high-speed memory caching for "sleek" backward/forward movement.

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/Naveenkumar-katomaran/ITMS-Inference-Tool.git
cd ITMS/video_inference_tool

# Install dependencies
pip install PyQt6 ultralytics opencv-python torch
```

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

## ⚙️ Configuration

The system uses `config.json` for all persistent settings. You can modify these directly or use the **SETTINGS** button in the UI:

- **Models**: Paths to your `.pt` model files.
- **Thresholds**: Independent confidence scores (0.0 to 1.0) for Vehicle, Plate, and OCR stages.
- **UI & Performance**:
  - `cache_limit`: Number of frames stored in memory for instant backward navigation.

## 📁 Project Structure

- `core/`: Inference engine, video handling, and workers.
- `ui/`: PyQt6 windows, widgets, and themes.
- `utils/`: Configuration and helper utilities.
- `models/`: Destination for AI model weights.

---
*Developed for Advanced Traffic Intelligence.*
