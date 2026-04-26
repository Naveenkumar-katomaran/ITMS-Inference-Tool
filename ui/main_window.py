import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QSlider, QLabel, QFileDialog, QToolBar, QStatusBar, QStyle, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence

from ui.video_widget import VideoWidget
from core.video_handler import VideoHandler
from core.inference import InferenceEngine
from core.overlay import OverlayManager
from core.worker import PlaybackThread, InferenceWorker, SeekWorker
from utils.config_loader import get_config
from ui.theme import Theme
from ui.settings_dialog import SettingsDialog
from utils.logger import logger as itms_logger
from utils.result_saver import saver as itms_saver
import cv2

class ClickableSlider(QSlider):
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            val = self.minimum() + ((self.maximum() - self.minimum()) * event.position().x()) / self.width()
            self.setValue(int(val))
            self.sliderMoved.emit(self.value())
        super().mousePressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.setWindowTitle("ITMS PRO | AI Surveillance")
        self.resize(1280, 850)

        # Apply Theme
        self.setStyleSheet(Theme.QSS)

        # Core components
        self.video_handler = VideoHandler()
        self.inference_engine = InferenceEngine()
        self.overlay_manager = OverlayManager()

        # State
        self.playback_thread = None
        self.inference_worker = None
        self.seek_worker = SeekWorker(self.video_handler)
        self.playback_speed = 1.0
        self.current_frame = None
        self.current_idx = 0

        self.init_ui()
        
        # Connect seek worker
        self.seek_worker.frame_ready.connect(self.on_frame_ready)
        self.seek_worker.start()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        def create_btn(text, callback):
            btn = QPushButton(text)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.clicked.connect(callback)
            return btn

        toolbar.addWidget(create_btn(" UPLOAD ", self.open_file))
        toolbar.addSeparator()
        toolbar.addWidget(create_btn(" INFER (I) ", self.start_inference))
        toolbar.addWidget(create_btn(" CLEAR (C) ", self.clear_overlay))
        toolbar.addSeparator()
        toolbar.addWidget(create_btn(" SETTINGS ", self.open_settings))
        toolbar.addSeparator()
        toolbar.addWidget(create_btn(" FULLSCREEN ", self.toggle_full_screen))

        # Main Viewport (Video)
        self.video_widget = VideoWidget()
        layout.addWidget(self.video_widget)

        # Bottom HUD Panel
        self.hud_panel = QWidget()
        self.hud_panel.setFixedHeight(80)
        self.hud_panel.setStyleSheet(f"background-color: {Theme.BG_MED}; border-top: 1px solid {Theme.BORDER};")
        hud_layout = QVBoxLayout(self.hud_panel)
        hud_layout.setContentsMargins(20, 5, 20, 10)

        # Slider
        self.slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.slider.sliderMoved.connect(self.seek_video)
        self.slider.sliderPressed.connect(self.pause_if_playing)
        hud_layout.addWidget(self.slider)

        # Controls Row
        controls_row = QHBoxLayout()
        self.play_btn = create_btn(" PLAY ", self.toggle_play)
        self.play_btn.setFixedWidth(80)
        controls_row.addWidget(self.play_btn)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet(f"color: {Theme.ACCENT}; font-weight: bold; font-family: monospace;")
        controls_row.addWidget(self.time_label)

        controls_row.addStretch()

        self.speed_btn = create_btn("1X SPEED", self.toggle_speed)
        controls_row.addWidget(self.speed_btn)

        hud_layout.addLayout(controls_row)
        layout.addWidget(self.hud_panel)

        # Status Bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("SYSTEM READY")

    def open_settings(self):
        self.config = get_config(reload=True)
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.inference_engine = InferenceEngine() 
            self.statusBar.showMessage("SETTINGS UPDATED & MODELS RELOADED")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Source", "", 
                                                  "Media (*.mp4 *.avi *.mkv *.jpg *.png)")
        if file_path:
            self.current_video_path = file_path
            self.stop_playback()
            if file_path.lower().endswith(('.jpg', '.png', '.jpeg')):
                img = cv2.imread(file_path)
                self.current_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                self.video_widget.set_frame(self.current_frame)
                self.video_widget.reset_zoom()
                self.slider.setEnabled(False)
                self.statusBar.showMessage(f"ANALYZING IMAGE: {os.path.basename(file_path)}")
            else:
                if self.video_handler.open_video(file_path):
                    self.current_frame = None
                    self.current_idx = 0
                    self.video_widget.set_frame(None)
                    self.slider.setEnabled(True)
                    self.slider.setRange(0, self.video_handler.frame_count - 1)
                    if self.playback_thread: self.playback_thread.stop()
                    self.playback_thread = PlaybackThread(self.video_handler)
                    self.playback_thread.frame_ready.connect(self.on_frame_ready)
                    self.seek_worker.reset_state()
                    self.seek_worker.seek_to(0)
                    self.video_widget.reset_zoom()
                    self.statusBar.showMessage(f"SOURCE LOADED: {os.path.basename(file_path)}")

    def toggle_play(self):
        if not self.playback_thread: return
        if self.playback_thread.isRunning():
            self.stop_playback()
        else:
            self.playback_thread.speed = self.playback_speed
            self.playback_thread.start()
            self.play_btn.setText(" PAUSE ")

    def stop_playback(self):
        if self.playback_thread and self.playback_thread.isRunning():
            self.playback_thread.stop()
            self.play_btn.setText(" PLAY ")

    def pause_if_playing(self):
        self.stop_playback()

    def on_frame_ready(self, frame, idx):
        self.current_frame = frame
        self.current_idx = idx
        self.update_ui_state()

    def update_ui_state(self):
        self.video_widget.set_frame(self.current_frame)
        self.slider.blockSignals(True)
        self.slider.setValue(self.current_idx)
        self.slider.blockSignals(False)
        
        cur_sec = int(self.current_idx / self.video_handler.fps) if self.video_handler.fps > 0 else 0
        tot_sec = int(self.video_handler.frame_count / self.video_handler.fps) if self.video_handler.fps > 0 else 0
        self.time_label.setText(f"{cur_sec//60:02d}:{cur_sec%60:02d} / {tot_sec//60:02d}:{tot_sec%60:02d}")

    def seek_video(self, position):
        self.seek_worker.seek_to(position)

    def update_frame(self, idx):
        self.seek_worker.seek_to(idx)

    def toggle_speed(self):
        speeds = [1.0, 2.0, 4.0]
        idx = speeds.index(self.playback_speed)
        self.playback_speed = speeds[(idx + 1) % len(speeds)]
        self.speed_btn.setText(f"{int(self.playback_speed)}X SPEED")
        if self.playback_thread:
            self.playback_thread.speed = self.playback_speed

    def start_inference(self):
        if self.current_frame is None: return
        self.stop_playback()
        self.statusBar.showMessage("WORKER: COMPUTING DETECTIONS...")
        
        # Capture current video millisecond
        msec = 0
        if hasattr(self, 'current_video_path') and not self.current_video_path.lower().endswith(('.jpg', '.png', '.jpeg')):
            msec = self.video_handler.cap.get(cv2.CAP_PROP_POS_MSEC)
            
        self.inference_worker = InferenceWorker(self.inference_engine, self.current_frame, msec)
        self.inference_worker.finished.connect(self.on_inference_finished)
        self.inference_worker.start()

    def on_inference_finished(self, detections, msec):
        overlay_frame = self.overlay_manager.draw_detections(self.current_frame, detections)
        self.video_widget.set_frame(overlay_frame)
        self.statusBar.showMessage("INFERENCE COMPLETE & LOGGED")
        
        # Logging and Saving
        vtime_formatted = self._format_vtime_mills(msec)
        vname = getattr(self, 'current_video_path', 'source')
        
        # Hierarchical Logging
        for v in detections:
            # 1. Log Vehicle
            itms_logger.log_detection(vname, vtime_formatted, "VEHICLE", v['label'], v['conf'], v['bbox'])
            
            # 2. Log Plates and Chars for this vehicle
            for p in v.get('plates', []):
                itms_logger.log_ocr_summary(vname, vtime_formatted, p['text'], p['text_conf'])
                itms_logger.log_detection(vname, vtime_formatted, "PLATE", p['label'], p['conf'], p['bbox'])
                for c in p.get('chars', []):
                    itms_logger.log_detection(vname, vtime_formatted, "CHAR", c['label'], c['conf'], c['bbox'])
            
            # 3. Add 5-line gap after each vehicle's data
            for _ in range(5):
                print("")
                if itms_logger.current_logger:
                    itms_logger.current_logger.info("")
        
        # Save results
        itms_saver.save_results(vname, self.current_frame, overlay_frame, msec, detections)

    def _format_vtime_mills(self, msec):
        seconds = int(msec // 1000)
        milliseconds = int(msec % 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

    def clear_overlay(self):
        if self.current_frame is not None:
            self.video_widget.set_frame(self.current_frame)

    def toggle_full_screen(self):
        if self.isFullScreen(): self.showNormal()
        else: self.showFullScreen()

    def closeEvent(self, event):
        if self.playback_thread: self.playback_thread.stop()
        if self.seek_worker: self.seek_worker.stop()
        super().closeEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        def is_key(binding_name):
            binding = self.config.get(f"keybindings.{binding_name}")
            if not binding: return False
            if isinstance(binding, list):
                return any(QKeySequence(b)[0].key() == key for b in binding)
            return QKeySequence(binding)[0].key() == key

        if is_key("play_pause"): self.toggle_play()
        elif is_key("next_frame") or key == Qt.Key.Key_Right: 
            self.stop_playback()
            self.update_frame(min(self.video_handler.frame_count-1, self.current_idx + 1))
        elif is_key("prev_frame") or key == Qt.Key.Key_Left: 
            self.stop_playback()
            self.update_frame(max(0, self.current_idx - 1))
        elif is_key("infer_frame"): self.start_inference()
        elif is_key("quit"): self.close()
        elif is_key("full_screen"): self.toggle_full_screen()
        elif is_key("upload_file"): self.open_file()
        elif is_key("clear_overlay"): self.clear_overlay()
        elif is_key("zoom_in") or key == Qt.Key.Key_Equal:
            self.video_widget.scale(1.25, 1.25)
            self.video_widget._zoom += 1
        elif is_key("zoom_out") or key == Qt.Key.Key_Minus:
            self.video_widget.scale(0.8, 0.8)
            self.video_widget._zoom -= 1
        elif is_key("reset_zoom"):
            self.video_widget.reset_zoom()
        else:
            super().keyPressEvent(event)
