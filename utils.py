from PySide6.QtGui import QPixmap, QPainter, QColor

def generate_checker_pixmap():
    """Generates a transparent background checkerboard pattern in memory"""
    size = 20
    pix = QPixmap(size * 2, size * 2)
    pix.fill(QColor(40, 40, 40))
    painter = QPainter(pix)
    painter.fillRect(0, 0, size, size, QColor(60, 60, 60))
    painter.fillRect(size, size, size, size, QColor(60, 60, 60))
    painter.end()
    return pix