import os
import cv2
from datetime import datetime
import uuid

class ResultSaver:
    def __init__(self):
        self.base_dir = "results"
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def _format_vtime(self, msec):
        """Converts milliseconds to HH_MM_SS_mmm format."""
        seconds = int(msec // 1000)
        milliseconds = int(msec % 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}_{minutes:02d}_{seconds:02d}_{milliseconds:03d}"

    def save_results(self, video_path, raw_frame, annotated_frame, msec, detections):
        """
        Saves full frame and plate crops into a unique folder per inference.
        """
        video_base = os.path.splitext(os.path.basename(video_path))[0]
        vtime_str = self._format_vtime(msec)
        unique_id = str(uuid.uuid4())[:8]
        
        # New Unque Folder: results/video_name/VTIME_UUID/
        inference_dir = os.path.join(self.base_dir, video_base, f"{vtime_str}_{unique_id}")
        if not os.path.exists(inference_dir):
            os.makedirs(inference_dir)
            
        # 1. Save Full Frame (Annotated with HUD)
        full_path = os.path.join(inference_dir, "full_view.jpg")
        bgr_annotated = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(full_path, bgr_annotated)
        
        # 2. Save Plate Crops from Raw Frame
        bgr_raw = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)
        
        plate_idx = 0
        for v in detections:
            for plate in v.get("plates", []):
                if plate.get("cls_idx") != 0: continue
                
                bbox = plate.get("bbox")
                if not bbox: continue
                
                x1, y1, x2, y2 = map(int, bbox)
                h, w = bgr_raw.shape[:2]
                x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
                
                plate_crop = bgr_raw[y1:y2, x1:x2].copy()
                if plate_crop.size > 0:
                    for char in plate.get("chars", []):
                        c_bbox = char.get("bbox")
                        cx1, cy1, cx2, cy2 = map(int, c_bbox)
                        rx1, ry1 = cx1 - x1, cy1 - y1
                        rx2, ry2 = cx2 - x1, cy2 - y1
                        cv2.rectangle(plate_crop, (rx1, ry1), (rx2, ry2), (0, 255, 0), 1)
                        cv2.putText(plate_crop, char['label'], (rx1, ry1 - 2), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                    
                    crop_filename = f"plate_{plate_idx}.jpg"
                    cv2.imwrite(os.path.join(inference_dir, crop_filename), plate_crop)
                    plate_idx += 1

# Global instance
saver = ResultSaver()
