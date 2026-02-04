import sys
from PIL import ImageQt
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QDockWidget, 
                               QListWidget, QWidget, QHBoxLayout, QPushButton, QLabel, QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap, QIcon

from config import STYLESHEET
from utils import generate_checker_pixmap
from core_ui import NodeScene
from nodes_lib import InputNode, OutputNode, NODE_REGISTRY

import ctypes, os

def resource_path(relative_path):
    try:
        # PYINStaller creats this _meipass thingo.
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PhotoNodes EX")
        self.resize(1400, 900)
        self.setStyleSheet(STYLESHEET)
        
        self.out_node = OutputNode(self.update_view)
        
        self.scene = NodeScene(self.out_node)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        
        # Gripe 1: Fix scrolling glitches
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        self.view.setDragMode(QGraphicsView.RubberBandDrag) 
        self.setCentralWidget(self.view)
        
        self.in_node = InputNode()
        self.in_node.setPos(100, 300)
        self.out_node.setPos(900, 300)
        self.scene.addItem(self.in_node)
        self.scene.addItem(self.out_node)
        
        self.setup_ui()
        self.current_img = None # Store for export

    def showEvent(self, event):
        super().showEvent(event)
        self.view.centerOn(500, 300)

    def setup_ui(self):
        # TOOLBOX
        d_tools = QDockWidget("Node Toolbox", self)
        lst = QListWidget()
        lst.addItems(sorted(NODE_REGISTRY.keys()))
        lst.itemDoubleClicked.connect(self.add_node)
        d_tools.setWidget(lst)
        self.addDockWidget(Qt.LeftDockWidgetArea, d_tools)
        
        # PREVIEW
        d_prev = QDockWidget("Preview", self)
        self.lbl = QLabel()
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setPixmap(generate_checker_pixmap())
        d_prev.setWidget(self.lbl)
        self.addDockWidget(Qt.RightDockWidgetArea, d_prev)
        
        # TOOLBAR
        bar = QWidget()
        l = QHBoxLayout()
        b_load = QPushButton("Load Image")
        b_load.clicked.connect(self.load_img)
        l.addWidget(b_load)
        
        # Gripe 3: Export Button
        b_save = QPushButton("Export Result")
        b_save.clicked.connect(self.save_img)
        l.addWidget(b_save)
        
        bar.setLayout(l)
        
        d_top = QDockWidget("Controls", self)
        d_top.setTitleBarWidget(QWidget())
        d_top.setWidget(bar)
        self.addDockWidget(Qt.TopDockWidgetArea, d_top)

    def add_node(self, item):
        node_class = NODE_REGISTRY.get(item.text())
        if node_class:
            node = node_class()
            node.setPos(self.view.mapToScene(self.view.viewport().rect().center()))
            self.scene.addItem(node)

    def load_img(self):
        p, _ = QFileDialog.getOpenFileName(self, "Load", "", "Img (*.png *.jpg *.jpeg)")
        if p:
            self.in_node.set_image(p)
            self.scene.trigger_eval()

    # Gripe 3: Export Logic
    def save_img(self):
        if not self.current_img: return
        p, _ = QFileDialog.getSaveFileName(self, "Save Image", "output.png", "PNG (*.png);;JPG (*.jpg)")
        if p:
            self.current_img.save(p)

    def update_view(self, img):
        self.current_img = img
        if not img: 
            self.lbl.setPixmap(generate_checker_pixmap())
            return
            
        im2 = img.convert("RGBA")
        data = im2.tobytes("raw", "RGBA")
        qim = ImageQt.QImage(data, im2.size[0], im2.size[1], ImageQt.QImage.Format_RGBA8888)
        pix = QPixmap.fromImage(qim)
        self.lbl.setPixmap(pix.scaled(self.lbl.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

if __name__ == "__main__":
    # this is to make it icon work on taskbar
    myappid = 'manikomtmn.photonodesEX.whatever'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    icon_path = resource_path("ICON.ico") 
    app.setWindowIcon(QIcon(icon_path))

    window = App()
    window.show()
    sys.exit(app.exec())