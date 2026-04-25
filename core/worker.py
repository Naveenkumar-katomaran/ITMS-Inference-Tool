import time
from PyQt6.QtCore import QThread, pyqtSignal, QMutex
import cv2

class PlaybackThread(QThread):
    frame_ready = pyqtSignal(object, int)  # frame, frame_idx

    def __init__(self, video_handler):
        super().__init__()
        self.video_handler = video_handler
        self.is_running = False
        self.speed = 1.0

    def run(self):
        self.is_running = True
        while self.is_running:
            start_time = time.time()
            
            frame = self.video_handler.get_frame()
            if frame is not None:
                self.frame_ready.emit(frame, self.video_handler.current_frame_idx - 1)
            else:
                self.is_running = False
                break
            
            # Control playback speed
            target_fps = self.video_handler.fps * self.speed
            if target_fps > 0:
                sleep_time = max(0, (1.0 / target_fps) - (time.time() - start_time))
                time.sleep(sleep_time)

    def stop(self):
        self.is_running = False
        self.wait()

class InferenceWorker(QThread):
    finished = pyqtSignal(object)  # detections

    def __init__(self, engine, frame):
        super().__init__()
        self.engine = engine
        self.frame = frame

    def run(self):
        detections = self.engine.run_inference(self.frame)
        self.finished.emit(detections)

class SeekWorker(QThread):
    """Handles asynchronous seeking to prevent UI lag."""
    frame_ready = pyqtSignal(object, int)

    def __init__(self, video_handler):
        super().__init__()
        self.video_handler = video_handler
        self.target_idx = -1
        self._running = True
        self._lock = QMutex()
        self.last_processed = -1

    def seek_to(self, idx):
        self._lock.lock()
        self.target_idx = idx
        self._lock.unlock()

    def reset_state(self):
        self._lock.lock()
        self.last_processed = -1
        self.target_idx = -1
        self._lock.unlock()

    def stop(self):
        self._running = False

    def run(self):
        while self._running:
            self._lock.lock()
            current_target = self.target_idx
            self._lock.unlock()

            if current_target != -1 and current_target != self.last_processed:
                if self.video_handler.seek(current_target):
                    frame = self.video_handler.get_frame()
                    if frame is not None:
                        self.frame_ready.emit(frame, current_target)
                self.last_processed = current_target
                continue
            
            self.msleep(5) 
