import json
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QDoubleSpinBox, QPushButton, QFormLayout)
from utils.config_loader import get_config
from ui.theme import Theme

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SYSTEM SETTINGS")
        self.setFixedWidth(450)
        self.config = get_config()
        self.config_path = "config.json"
        
        self.init_ui()
        self.setStyleSheet(Theme.QSS)

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Models Section
        model_label = QLabel("MODEL CONFIGURATION")
        model_label.setStyleSheet(f"color: {Theme.ACCENT}; font-weight: bold; margin-top: 10px;")
        form_layout.addRow(model_label)
        
        self.v_model_edit = QLineEdit(self.config.get("models.vehicle_detection"))
        self.p_model_edit = QLineEdit(self.config.get("models.plate_detection"))
        self.o_model_edit = QLineEdit(self.config.get("models.ocr"))
        
        form_layout.addRow("Vehicle Model:", self.v_model_edit)
        form_layout.addRow("Plate Model:", self.p_model_edit)
        form_layout.addRow("OCR Model:", self.o_model_edit)
        
        # Thresholds Section
        thresh_label = QLabel("CONFIDENCE THRESHOLDS")
        thresh_label.setStyleSheet(f"color: {Theme.ACCENT}; font-weight: bold; margin-top: 10px;")
        form_layout.addRow(thresh_label)
        
        self.v_thresh_spin = QDoubleSpinBox()
        self.v_thresh_spin.setRange(0.0, 1.0)
        self.v_thresh_spin.setSingleStep(0.05)
        self.v_thresh_spin.setValue(self.config.get("inference.vehicle_threshold", 0.5))
        
        self.p_thresh_spin = QDoubleSpinBox()
        self.p_thresh_spin.setRange(0.0, 1.0)
        self.p_thresh_spin.setSingleStep(0.05)
        self.p_thresh_spin.setValue(self.config.get("inference.plate_threshold", 0.3))
        
        self.o_thresh_spin = QDoubleSpinBox()
        self.o_thresh_spin.setRange(0.0, 1.0)
        self.o_thresh_spin.setSingleStep(0.05)
        self.o_thresh_spin.setValue(self.config.get("inference.ocr_threshold", 0.3))
        
        form_layout.addRow("Vehicle Thresh:", self.v_thresh_spin)
        form_layout.addRow("Plate Thresh:", self.p_thresh_spin)
        form_layout.addRow("OCR Thresh:", self.o_thresh_spin)
        
        # UI Section
        ui_label = QLabel("UI & PERFORMANCE")
        ui_label.setStyleSheet(f"color: {Theme.ACCENT}; font-weight: bold; margin-top: 10px;")
        form_layout.addRow(ui_label)
        
        self.cache_spin = QDoubleSpinBox() # Using Double but as int
        self.cache_spin.setRange(10, 500)
        self.cache_spin.setDecimals(0)
        self.cache_spin.setValue(self.config.get("ui.cache_limit", 50))
        form_layout.addRow("Backstep Cache:", self.cache_spin)

        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("SAVE SETTINGS")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_settings(self):
        # Update config object in memory
        new_config = {
            "models": {
                "vehicle_detection": self.v_model_edit.text(),
                "plate_detection": self.p_model_edit.text(),
                "ocr": self.o_model_edit.text()
            },
            "inference": {
                "vehicle_threshold": self.v_thresh_spin.value(),
                "plate_threshold": self.p_thresh_spin.value(),
                "ocr_threshold": self.o_thresh_spin.value(),
                "device": self.config.get("inference.device", "cpu")
            },
            "ui": {
                "default_speed": self.config.get("ui.default_speed", 1.0),
                "zoom_step": self.config.get("ui.zoom_step", 0.2),
                "cache_limit": int(self.cache_spin.value())
            },
            "keybindings": self.config.get("keybindings")
        }
        
        # Save to file
        with open(self.config_path, "w") as f:
            json.dump(new_config, f, indent=4)
            
        self.accept()
