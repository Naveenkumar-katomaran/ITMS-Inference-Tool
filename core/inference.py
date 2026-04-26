import os
from ultralytics import YOLO
import torch
import numpy as np
from utils.config_loader import get_config

from utils.paths import resolve_path

class InferenceEngine:
    def __init__(self):
        self.config = get_config()
        self.device = self.config.get("inference.device", "cpu")
        self.conf_threshold = self.config.get("inference.confidence_threshold", 0.3)
        
        # Paths - Resolved relative to application root
        vehicle_path = resolve_path(self.config.get("models.vehicle_detection"))
        plate_path = resolve_path(self.config.get("models.plate_detection"))
        ocr_path = resolve_path(self.config.get("models.ocr"))

        # Load models
        self.vehicle_model = YOLO(vehicle_path)
        self.plate_model = YOLO(plate_path)
        self.ocr_model = YOLO(ocr_path)
        
        # Move models to device
        self.vehicle_model.to(self.device)
        self.plate_model.to(self.device)
        self.ocr_model.to(self.device)

        # Load dynamic labels
        self.vehicle_labels = self.load_labels(os.path.dirname(vehicle_path))
        self.plate_labels = self.load_labels(os.path.dirname(plate_path))
        self.ocr_labels = self.load_labels(os.path.dirname(ocr_path))

    def load_labels(self, model_dir):
        """Loads classes.txt and infer_labels.txt from the model directory."""
        classes_file = os.path.join(model_dir, "classes.txt")
        infer_file = os.path.join(model_dir, "infer_labels.txt")
        
        all_classes = []
        if os.path.exists(classes_file):
            with open(classes_file, "r") as f:
                all_classes = [line.strip() for line in f if line.strip()]
        
        infer_labels = set()
        if os.path.exists(infer_file):
            with open(infer_file, "r") as f:
                infer_labels = {line.strip() for line in f if line.strip()}
        
        return {
            "all": all_classes,
            "whitelist": infer_labels
        }

    def get_label(self, cls_idx, label_config, model_names):
        """Gets label name if it's in the whitelist, else None."""
        # Use classes.txt if provided, otherwise fallback to model.names
        if label_config["all"]:
            label = label_config["all"][cls_idx] if cls_idx < len(label_config["all"]) else "unknown"
        else:
            label = model_names[cls_idx]
            
        if not label_config["whitelist"] or label in label_config["whitelist"]:
            return label
        return None

    def run_inference(self, frame):
        results = []
        
        # Thresholds
        v_thresh = self.config.get("inference.vehicle_threshold", 0.5)
        p_thresh = self.config.get("inference.plate_threshold", 0.3)
        o_thresh = self.config.get("inference.ocr_threshold", 0.3)

        # 1. Vehicle Detection - Full Frame
        vehicle_results = self.vehicle_model(frame, conf=v_thresh, verbose=False)[0]
        
        for box in vehicle_results.boxes:
            v_cls = int(box.cls[0].cpu().numpy())
            v_label = self.get_label(v_cls, self.vehicle_labels, self.vehicle_model.names)
            
            if v_label is None: continue

            xv1, yv1, xv2, yv2 = map(int, box.xyxy[0].cpu().numpy())
            v_conf = box.conf[0].cpu().numpy()
            
            vehicle_data = {
                "bbox": [xv1, yv1, xv2, yv2],
                "conf": v_conf,
                "label": v_label,
                "type": "vehicle",
                "plates": []
            }

            # 2. Plate Detection - Within Vehicle Crop
            xv1, yv1, xv2, yv2 = max(0, xv1), max(0, yv1), min(frame.shape[1], xv2), min(frame.shape[0], yv2)
            vehicle_crop = frame[yv1:yv2, xv1:xv2]
            if vehicle_crop.size > 0:
                plate_results = self.plate_model(vehicle_crop, conf=p_thresh, verbose=False)[0]
                for p_box in plate_results.boxes:
                    p_cls = int(p_box.cls[0].cpu().numpy())
                    p_label = self.get_label(p_cls, self.plate_labels, self.plate_model.names)
                    
                    if p_label is None: continue

                    xp1, yp1, xp2, yp2 = map(int, p_box.xyxy[0].cpu().numpy())
                    p_conf = p_box.conf[0].cpu().numpy()
                    
                    full_xp1, full_yp1 = xv1 + xp1, yv1 + yp1
                    full_xp2, full_yp2 = xv1 + xp2, yv1 + yp2
                    
                    # 3. OCR - Within Plate Crop
                    plate_crop = vehicle_crop[yp1:yp2, xp1:xp2]
                    combined_text = ""
                    avg_conf = 0
                    chars = []
                    
                    if plate_crop.size > 0:
                        ocr_results = self.ocr_model(plate_crop, conf=o_thresh, verbose=False)[0]
                        for o_box in ocr_results.boxes:
                            o_cls = int(o_box.cls[0].cpu().numpy())
                            o_label = self.get_label(o_cls, self.ocr_labels, self.ocr_model.names)
                            
                            if o_label is None: continue

                            co1, co2, co3, co4 = map(int, o_box.xyxy[0].cpu().numpy())
                            o_conf = o_box.conf[0].cpu().numpy()
                            
                            chars.append({
                                "label": o_label,
                                "conf": o_conf,
                                "bbox": [full_xp1 + co1, full_yp1 + co2, full_xp1 + co3, full_yp1 + co4],
                                "x_rel": co1
                            })
                        
                        if chars:
                            chars.sort(key=lambda x: x["x_rel"])
                            combined_text = "".join(c["label"] for c in chars)
                            avg_conf = sum(c["conf"] for c in chars) / len(chars)

                    vehicle_data["plates"].append({
                        "bbox": [full_xp1, full_yp1, full_xp2, full_yp2],
                        "conf": p_conf,
                        "label": p_label,
                        "text": combined_text,
                        "text_conf": avg_conf,
                        "chars": chars,
                        "cls_idx": p_cls,
                        "type": "plate"
                    })
            
            results.append(vehicle_data)
            
        return results
