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
        CYAN = (0, 249, 255)
        GREEN = (0, 255, 127)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_thickness = 1
        font_scale_name = 0.6
        font_scale_pixel = 0.4
        
        for v in detections:
            v_color = GREEN
            vx1, vy1, vx2, vy2 = map(int, v["bbox"])
            vw, vh = vx2 - vx1, vy2 - vy1
            
            # Draw Vehicle
            cv2.rectangle(overlay, (vx1, vy1), (vx2, vy2), (0, 0, 0), 4)
            cv2.rectangle(overlay, (vx1, vy1), (vx2, vy2), v_color, 2)
            
            v_name = f"{v['label'].upper()} {v['conf']:.2f}"
            v_pixel = f"W:{vw} H:{vh}"
            
            # Label background calc
            (tw1, th1), _ = cv2.getTextSize(v_name, font, font_scale_name, text_thickness)
            (tw2, th2), _ = cv2.getTextSize(v_pixel, font, font_scale_pixel, text_thickness)
            max_tw = max(tw1, tw2)
            total_th = th1 + th2 + 10
            
            cv2.rectangle(overlay, (vx1 - 2, vy1 - total_th - 5), (vx1 + max_tw + 12, vy1 + 2), (0, 0, 0), -1)
            cv2.rectangle(overlay, (vx1, vy1 - total_th - 3), (vx1 + max_tw + 10, vy1), v_color, -1)
            cv2.putText(overlay, v_name, (vx1 + 5, vy1 - th2 - 12), font, font_scale_name, (255, 255, 255), text_thickness, cv2.LINE_AA)
            cv2.putText(overlay, v_pixel, (vx1 + 5, vy1 - 5), font, font_scale_pixel, (255, 255, 255), text_thickness, cv2.LINE_AA)

            # Draw Plates for this vehicle
            for p in v.get("plates", []):
                p_color = CYAN
                px1, py1, px2, py2 = map(int, p["bbox"])
                pw, ph = px2 - px1, py2 - py1
                
                cv2.rectangle(overlay, (px1, py1), (px2, py2), (0, 0, 0), 4)
                cv2.rectangle(overlay, (px1, py1), (px2, py2), p_color, 2)
                
                p_name = f"{p['label'].upper()} {p['conf']:.2f}"
                if p.get("text"): p_name = f"{p['text']} | {p_name}"
                p_pixel = f"W:{pw} H:{ph}"
                
                (tw1, th1), _ = cv2.getTextSize(p_name, font, font_scale_name, text_thickness)
                (tw2, th2), _ = cv2.getTextSize(p_pixel, font, font_scale_pixel, text_thickness)
                max_tw = max(tw1, tw2)
                total_th = th1 + th2 + 10

                cv2.rectangle(overlay, (px1 - 2, py1 - total_th - 5), (px1 + max_tw + 12, py1 + 2), (0, 0, 0), -1)
                cv2.rectangle(overlay, (px1, py1 - total_th - 3), (px1 + max_tw + 10, py1), p_color, -1)
                cv2.putText(overlay, p_name, (px1 + 5, py1 - th2 - 12), font, font_scale_name, (255, 255, 255), text_thickness, cv2.LINE_AA)
                cv2.putText(overlay, p_pixel, (px1 + 5, py1 - 5), font, font_scale_pixel, (255, 255, 255), text_thickness, cv2.LINE_AA)

        return overlay
        
        return overlay
