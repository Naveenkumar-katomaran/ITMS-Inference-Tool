import os
import logging
from datetime import datetime

class ITMSLogger:
    def __init__(self):
        self.base_dir = "logs"
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        self.current_logger = None
        self.current_file = None

    def _setup_logger(self, video_name):
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_dir = os.path.join(self.base_dir, date_str)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        video_base = os.path.splitext(os.path.basename(video_name))[0]
        log_file = os.path.join(log_dir, f"{video_base}.log")
        
        # Simple logger setup
        logger = logging.getLogger(video_base)
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers if any
        if logger.hasHandlers():
            logger.handlers.clear()
            
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        self.current_logger = logger
        self.current_file = log_file

    def log_ocr_summary(self, video_name, timestamp_str, plate_text, conf):
        """Logs the final aggregated OCR text."""
        if self.current_logger is None or self.current_file is None or video_name not in self.current_file:
            self._setup_logger(video_name)
            
        log_line = f"INFO | [{timestamp_str}] [OCR RESULT] PLATE TEXT: {plate_text} (Conf: {conf:.2f})"
        print(log_line)
        if self.current_logger:
            self.current_logger.info(log_line)

    def log_detection(self, video_name, timestamp_str, det_type, label, conf, bbox):
        """
        Logs a detection in the standard format.
        bbox should be [x1, y1, x2, y2]
        """
        if self.current_logger is None or self.current_file is None or video_name not in self.current_file:
            self._setup_logger(video_name)
            
        x1, y1, x2, y2 = bbox
        w = x2 - x1
        h = y2 - y1
        area = w * h
        
        log_line = f"INFO | [{timestamp_str}] [PIXEL DETAIL] {det_type}: {label} ({conf:.2f}) @ [{x1}, {y1}, {x2}, {y2}] | W:{w} H:{h} Area:{area}"
        
        # Print to terminal for real-time review
        print(log_line)
        
        # Write to file
        if self.current_logger:
            self.current_logger.info(log_line)

# Global instance for easy access
logger = ITMSLogger()
