from PySide6.QtGui import QColor

# ====================
# colors (ue5 style)
# ====================
C_BG_APP     = QColor(15, 15, 15)
C_BG_VIEW    = QColor(25, 25, 25)
C_GRID_LINES = QColor(40, 40, 40)

# node colors
C_NODE_BODY    = QColor(20, 20, 20, 200) # semi-transparent dark
C_NODE_BORDER  = QColor(10, 10, 10)
C_NODE_SEL     = QColor(255, 200, 0)     # golden yellow selection

# header colors
C_HEADER_DEFAULT = QColor(50, 50, 50)
C_HEADER_FUNC    = QColor(40, 100, 150)
C_HEADER_EVENT   = QColor(150, 40, 40)

# text
C_TEXT_MAIN  = QColor(220, 220, 220)
C_TEXT_TITLE = QColor(255, 255, 255)

# socket types
C_TYPE_IMAGE = QColor(255, 50, 100)
C_TYPE_FLOAT = QColor(100, 255, 100)
C_TYPE_COLOR = QColor(50, 150, 255)
C_TYPE_ANY   = QColor(180, 180, 180)

# ====================
# stylesheet
# ====================
STYLESHEET = """
QMainWindow { background-color: #0f0f0f; color: #ddd; }
QDockWidget { font-family: "Segoe UI"; color: #ddd; font-weight: bold; }
QDockWidget::title { background: #1a1a1a; padding: 6px; border-bottom: 1px solid #333; }

QScrollBar:vertical { border: none; background: #222; width: 10px; margin: 0px; }
QScrollBar::handle:vertical { background: #444; min-height: 20px; border-radius: 5px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar:horizontal { border: none; background: #222; height: 10px; margin: 0px; }
QScrollBar::handle:horizontal { background: #444; min-width: 20px; border-radius: 5px; }

QLineEdit { 
    background: #000; color: #eee; 
    border: 1px solid #444; border-radius: 4px; 
    font-family: Consolas; font-size: 11px; padding: 2px; 
}
QLineEdit:disabled { background: #222; color: #555; border: 1px solid #222; }

QListWidget { background: #1a1a1a; border: none; font-size: 13px; color: #ccc; outline: none; }
QListWidget::item { padding: 8px; border-bottom: 1px solid #252525; }
QListWidget::item:hover { background: #333; }
QListWidget::item:selected { background: #0078d7; color: white; }

QPushButton { background: #333; color: white; border: 1px solid #222; padding: 6px; border-radius: 4px; }
QPushButton:hover { background: #444; }
QPushButton:pressed { background: #222; }

QLineEdit { 
    background: #111; color: #eee; 
    border: 1px solid #333; border-radius: 4px; 
    font-family: Consolas; font-size: 11px; padding: 2px 4px; 
}
QLineEdit:focus {
    border: 1px solid #0078d7; background: #000;
}
QLineEdit:disabled { background: #222; color: #555; border: 1px solid #222; }
"""