from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QGraphicsProxyWidget, QLineEdit, QGraphicsScene, QGraphicsView
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPainterPath, QPen, QBrush, QLinearGradient, QFont, QDoubleValidator, QFontMetrics
from config import *

# ==========================================
# socket
# ==========================================
class Socket(QGraphicsItem):
    def __init__(self, parent, socket_type, name, data_type, index=0):
        super().__init__(parent)
        self.parent_node = parent
        self.socket_type = socket_type
        self.name = name
        self.data_type = data_type
        self.connected_edges = [] 
        self.setAcceptHoverEvents(True)
        
        self.color = C_TYPE_ANY
        if data_type == "IMAGE": self.color = C_TYPE_IMAGE
        elif data_type == "FLOAT": self.color = C_TYPE_FLOAT
        elif data_type == "COLOR": self.color = C_TYPE_COLOR

        # layout logic handles the x position dynamically now based on parent width
        self.index = index
        self.update_pos()

    def update_pos(self):
        # helper to reset position if node width changes
        y = 50 + (self.index * 28)
        x = -8 if self.socket_type == "input" else self.parent_node.width + 8
        self.setPos(x, y)

    def boundingRect(self):
        return QRectF(-8, -8, 16, 16)

    def paint(self, painter, option, widget):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 1.5))
        painter.drawEllipse(-5, -5, 10, 10)
        
        painter.setPen(C_TEXT_MAIN)
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        if self.socket_type == "input":
            painter.drawText(QRectF(15, -7, 100, 14), Qt.AlignLeft | Qt.AlignVCenter, self.name)
        else:
            painter.drawText(QRectF(-115, -7, 100, 14), Qt.AlignRight | Qt.AlignVCenter, self.name)

# ==========================================
# edge
# ==========================================
class Edge(QGraphicsPathItem):
    def __init__(self, start_socket, drag_pos=None):
        super().__init__()
        self.start_socket = start_socket
        self.end_socket = None
        self.drag_pos = drag_pos if drag_pos else QPointF(0,0)
        self.setZValue(-1)
        self.update_path()

    def update_path(self):
        if not self.start_socket: return
        start = self.start_socket.scenePos()
        end = self.end_socket.scenePos() if self.end_socket else self.drag_pos
        
        path = QPainterPath()
        path.moveTo(start)
        
        dx = abs(end.x() - start.x())
        ctrl_dist = dx * 0.5 if dx > 50 else 50
        
        path.cubicTo(start.x() + ctrl_dist, start.y(), 
                     end.x() - ctrl_dist, end.y(), 
                     end.x(), end.y())
        self.setPath(path)

    def paint(self, painter, option, widget):
        col = self.start_socket.color if self.start_socket else C_TYPE_ANY
        if self.isSelected(): col = C_NODE_SEL
        
        pen = QPen(col, 2.5)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPath(self.path())

# ==========================================
# base node
# ==========================================
class BaseNode(QGraphicsItem):
    def __init__(self, name="Node", width=165, header_color=C_HEADER_DEFAULT):
        super().__init__()
        self.name = name
        self.width = width
        self.header_color = header_color
        self.height = 60
        self.inputs = []
        self.outputs = []
        self.input_widgets = {} 
        
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemSendsGeometryChanges)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for s in self.inputs + self.outputs:
                for edge in s.connected_edges:
                    edge.update_path()
        return super().itemChange(change, value)

    def add_input(self, name, data_type="ANY", default_val=None):
        idx = len(self.inputs)
        
        # calculate width needed for label
        font = QFont("Segoe UI", 8, QFont.Bold)
        fm = QFontMetrics(font)
        text_w = fm.horizontalAdvance(name)
        
        has_widget = False
        widget_w = 0
        
        if data_type in ["FLOAT", "INT"] and default_val is not None:
            has_widget = True
            widget_w = 60
        
        # calc required width: margin + text + space + widget + safety for output label (50px)
        req_w = 20 + text_w + 10 + widget_w + 50 
        
        # resize node if too small
        if req_w > self.width:
            self.width = req_w
            # update output socket positions since width changed
            for out in self.outputs: out.update_pos()
            # update existing input sockets (visual cleanup)
            for inp in self.inputs: inp.update_pos()

        s = Socket(self, "input", name, data_type, idx)
        self.inputs.append(s)
        
        if has_widget:
            txt = QLineEdit(str(default_val))
            txt.setValidator(QDoubleValidator())
            txt.setAlignment(Qt.AlignLeft) # align left looks better now
            txt.setFixedWidth(widget_w)
            txt.textChanged.connect(lambda: self.scene().trigger_eval() if self.scene() else None)
            
            proxy = QGraphicsProxyWidget(self)
            proxy.setWidget(txt)
            
            # place widget immediately after the text label (approx 25px offset for socket + margin)
            proxy.setPos(25 + text_w + 10, 41 + (idx * 28))
            proxy.setZValue(10)
            self.input_widgets[idx] = (txt, proxy)
        
        self.update_height()
        return s

    def add_output(self, name, data_type="ANY"):
        s = Socket(self, "output", name, data_type, len(self.outputs))
        self.outputs.append(s)
        self.update_height()
        return s

    def update_height(self):
        m = max(len(self.inputs), len(self.outputs))
        self.height = 50 + (m * 28) + 10

    def get_input_val(self, index, default=None):
        if index < len(self.inputs):
            sock = self.inputs[index]
            if sock.connected_edges:
                edge = sock.connected_edges[0] 
                if edge.start_socket:
                    val = edge.start_socket.parent_node.eval()
                    if val is not None: return val
        
        if index in self.input_widgets:
            widget, _ = self.input_widgets[index]
            try: return float(widget.text())
            except: pass
            
        return default
        
    def update_widgets(self):
        for idx, (widget, _) in self.input_widgets.items():
            sock = self.inputs[idx]
            widget.setDisabled(bool(sock.connected_edges))

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        # header path
        # combine a rounded rect and a square rect at the bottom to ensure no gaps
        path_header = QPainterPath()
        path_header.addRoundedRect(0, 0, self.width, 30, 8, 8)
        path_header.addRect(0, 20, self.width, 10) 
        path_header.setFillRule(Qt.WindingFill)
        
        grad = QLinearGradient(0, 0, 0, 30)
        grad.setColorAt(0, self.header_color.lighter(120))
        grad.setColorAt(1, self.header_color)
        
        painter.setBrush(grad)
        painter.setPen(Qt.NoPen)
        painter.drawPath(path_header)

        # body path
        path_body = QPainterPath()
        path_body.addRoundedRect(0, 30, self.width, self.height - 30, 8, 8)
        path_body.addRect(0, 30, self.width, 10) 
        path_body.setFillRule(Qt.WindingFill)
        
        painter.setBrush(C_NODE_BODY)
        painter.drawPath(path_body)

        # outline
        color = C_NODE_SEL if self.isSelected() else C_NODE_BORDER
        width = 2 if self.isSelected() else 1
        painter.setPen(QPen(color, width))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(0, 0, self.width, self.height, 8, 8)

        # title
        painter.setPen(C_TEXT_TITLE)
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.drawText(QRectF(10, 0, self.width - 20, 30), Qt.AlignVCenter, self.name.upper())

    def eval(self): return None

# ==========================================
# scene
# ==========================================
class NodeScene(QGraphicsScene):
    def __init__(self, output_node):
        super().__init__()
        self.output_node = output_node
        self.active_edge = None
        self.setSceneRect(0, 0, 5000, 5000)
        self.setBackgroundBrush(QBrush(C_BG_VIEW))

    def trigger_eval(self):
        for item in self.items():
            if isinstance(item, BaseNode):
                item.update_widgets()
        if self.output_node: self.output_node.refresh()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for item in self.selectedItems():
                if isinstance(item, BaseNode):
                    if hasattr(item, "is_permanent") and item.is_permanent: continue
                    for s in item.inputs + item.outputs:
                        for edge in list(s.connected_edges):
                            self.remove_edge(edge)
                    self.removeItem(item)
                elif isinstance(item, Edge):
                    self.remove_edge(item)
            self.trigger_eval()
        super().keyPressEvent(event)

    def remove_edge(self, edge):
        if edge.start_socket and edge in edge.start_socket.connected_edges:
            edge.start_socket.connected_edges.remove(edge)
        if edge.end_socket and edge in edge.end_socket.connected_edges:
            edge.end_socket.connected_edges.remove(edge)
        self.removeItem(edge)
        self.trigger_eval()

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), self.views()[0].transform())
        
        if isinstance(item, Socket):
            if self.views(): self.views()[0].setDragMode(QGraphicsView.NoDrag)
            if item.socket_type == "output":
                self.active_edge = Edge(item, drag_pos=event.scenePos())
                self.addItem(self.active_edge)
            event.accept()
        else:
            if self.views(): self.views()[0].setDragMode(QGraphicsView.RubberBandDrag)
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.active_edge:
            self.active_edge.drag_pos = event.scenePos()
            self.active_edge.update_path()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.active_edge:
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            if isinstance(item, Socket) and item.socket_type == "input":
                if self.active_edge.start_socket.data_type == item.data_type or item.data_type == "ANY":
                    if item.connected_edges: self.remove_edge(item.connected_edges[0])
                    self.active_edge.end_socket = item
                    self.active_edge.start_socket.connected_edges.append(self.active_edge)
                    item.connected_edges.append(self.active_edge)
                    self.active_edge.update_path()
                    self.trigger_eval()
                else:
                    self.removeItem(self.active_edge)
            else:
                self.removeItem(self.active_edge)
            self.active_edge = None
            if self.views(): self.views()[0].setDragMode(QGraphicsView.RubberBandDrag)
        super().mouseReleaseEvent(event)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        pen = QPen(C_GRID_LINES, 1)
        painter.setPen(pen)
        grid = 50
        l = int(rect.left()) - (int(rect.left()) % grid)
        t = int(rect.top()) - (int(rect.top()) % grid)
        for x in range(l, int(rect.right()), grid): painter.drawLine(x, rect.top(), x, rect.bottom())
        for y in range(t, int(rect.bottom()), grid): painter.drawLine(rect.left(), y, rect.right(), y)