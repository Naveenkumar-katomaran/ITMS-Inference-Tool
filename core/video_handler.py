import cv2
import os
from PyQt6.QtCore import QMutex, QMutexLocker
from utils.config_loader import get_config

class VideoHandler:
    def __init__(self):
        self.cap = None
        self.filepath = None
        self.frame_count = 0
        self.fps = 0
        self.width = 0
        self.height = 0
        self.current_frame_idx = 0
        self.mutex = QMutex()
        
        # Simple FIFO Cache for backward stepping
        self.cache = {}
        self.config = get_config()
        self.cache_limit = self.config.get("ui.cache_limit", 50)

    def open_video(self, filepath):
        locker = QMutexLocker(self.mutex)
        if not os.path.exists(filepath):
            return False
        
        self.filepath = filepath
        self.cap = cv2.VideoCapture(filepath)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.current_frame_idx = 0
        self.cache.clear()
        return True

    def get_frame(self, frame_idx=None):
        locker = QMutexLocker(self.mutex)
        if self.cap is None:
            return None
        
        idx_to_read = frame_idx if frame_idx is not None else self.current_frame_idx
        
        # Check cache
        if idx_to_read in self.cache:
            self.current_frame_idx = idx_to_read + 1
            return self.cache[idx_to_read]
        
        # Random access if specifically requested
        if frame_idx is not None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            self.current_frame_idx = frame_idx
            
        ret, frame = self.cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Store in cache
            self.cache[self.current_frame_idx] = rgb_frame
            if len(self.cache) > self.cache_limit:
                # Remove oldest (roughly)
                first_key = next(iter(self.cache))
                del self.cache[first_key]
                
            self.current_frame_idx += 1
            return rgb_frame
        return None

    def seek(self, frame_idx):
        locker = QMutexLocker(self.mutex)
        if not self.cap or frame_idx < 0 or frame_idx >= self.frame_count:
            return False
            
        # Optimization: If in cache, we don't even need to tell OpenCV
        if frame_idx in self.cache:
            self.current_frame_idx = frame_idx
            return True

        # Optimization: If moving to the immediate next frame, we rely on read()
        if frame_idx == self.current_frame_idx:
            return True

        # Standard seek
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        self.current_frame_idx = frame_idx
        return True

    def close(self):
        locker = QMutexLocker(self.mutex)
        if self.cap:
            self.cap.release()
            self.cap = None
        self.cache.clear()
