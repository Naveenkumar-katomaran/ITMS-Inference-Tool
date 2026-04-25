import cv2
import numpy as np

class OverlayManager:
    @staticmethod
    def draw_detections(frame, detections):
        """
        Draws HUD-style bounding boxes and labels on the frame.
        """
        overlay = frame.copy()
        
        # Cyber HUD Colors (RGB)
        colors = {
            "vehicle": (255, 249, 0),  # Cyan-ish (translated from BGR/RGB thoughts, let's use actual Cyan: 0, 249, 255)
            "plate": (0, 0, 255),    # Red
        }
        
        # Correcting order for RGB (OpenCV expects RGB here because I convert it in video_handler)
        # But wait, video_handler returns RGB. cv2 drawing functions expect (B, G, R).
        # Let's check main_window: set_frame uses Format_RGB888. 
        # So I should define colors as (R, G, B) if I'm drawing on an RGB frame.
        
        CYAN = (0, 249, 255)
        RED = (255, 64, 129)
        GREEN = (0, 255, 127)
        
        type_colors = {
            "vehicle": GREEN,
            "plate": CYAN,
        }
        
        for category, items in detections.items():
            color = type_colors.get(category[:-1] if category.endswith('s') else category, CYAN)
            for item in items:
                x1, y1, x2, y2 = map(int, item["bbox"])
                conf = item["conf"]
                label = item["label"]
                
                # High-Contrast Bounding Box (Black outline + Color inner)
                cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), 4)
                cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
                
                # Prepare text
                display_text = f"{label.upper()} {conf:.2f}"
                if category == "plates" and item.get("text"):
                    display_text = f"{item['text']} | {display_text}"
                
                # Label positioning and sizing
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.7 # Slightly larger as requested
                text_thickness = 2
                (tw, th), baseline = cv2.getTextSize(display_text, font, font_scale, text_thickness)
                
                # Draw label background with black border
                cv2.rectangle(overlay, (x1 - 2, y1 - th - 12), (x1 + tw + 12, y1 + 2), (0, 0, 0), -1)
                cv2.rectangle(overlay, (x1, y1 - th - 10), (x1 + tw + 10, y1), color, -1)
                
                # Draw text with high contrast
                cv2.putText(overlay, display_text, (x1 + 5, y1 - 7), font, font_scale, (255, 255, 255), text_thickness, cv2.LINE_AA)
        
        return overlay
