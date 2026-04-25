from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

class Theme:
    # Color Palette
    BG_DARK = "#0F111A"
    BG_MED = "#1A1D2B"
    ACCENT = "#00F9FF"  # Cyber Cyan
    TEXT_PRIMARY = "#E0E0E0"
    TEXT_SECONDARY = "#90A4AE"
    BORDER = "#2E3248"
    
    QSS = f"""
    QMainWindow {{
        background-color: {BG_DARK};
    }}
    
    QWidget {{
        background-color: {BG_DARK};
        color: {TEXT_PRIMARY};
        font-family: 'Segoe UI', sans-serif;
        font-size: 13px;
    }}
    
    QToolBar {{
        background-color: {BG_MED};
        border-bottom: 1px solid {BORDER};
        spacing: 15px;
        padding: 5px;
    }}
    
    QPushButton {{
        background-color: {BG_MED};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 15px;
        color: {TEXT_PRIMARY};
    }}
    
    QPushButton:hover {{
        background-color: {BORDER};
        border-color: {ACCENT};
    }}
    
    QPushButton:pressed {{
        background-color: {ACCENT};
        color: {BG_DARK};
    }}
    
    QSlider::groove:horizontal {{
        border: 1px solid {BORDER};
        height: 6px;
        background: {BG_MED};
        margin: 2px 0;
        border-radius: 3px;
    }}

    QSlider::sub-page:horizontal {{
        background: {ACCENT};
        border-radius: 3px;
    }}

    QSlider::handle:horizontal {{
        background: {ACCENT};
        border: 1px solid {ACCENT};
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 8px;
    }}
    
    QStatusBar {{
        background-color: {BG_MED};
        color: {TEXT_SECONDARY};
        border-top: 1px solid {BORDER};
    }}
    
    QLabel {{
        background: transparent;
    }}
    """

    @staticmethod
    def apply_palette(app):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(Theme.BG_DARK))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(Theme.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.Base, QColor(Theme.BG_MED))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(Theme.BG_DARK))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(Theme.ACCENT))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(Theme.BG_DARK))
        palette.setColor(QPalette.ColorRole.Text, QColor(Theme.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.Button, QColor(Theme.BG_MED))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(Theme.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Link, QColor(Theme.ACCENT))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(Theme.ACCENT))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(Theme.BG_DARK))
        app.setPalette(palette)
