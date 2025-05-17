# -*- coding: utf-8 -*-
"""Widget de Canvas para desenho colaborativo."""

from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPolygonF
from PySide6.QtCore import Qt, QPointF, QRectF, QTimer
from client.services.supabase_client import get_supabase_client
import uuid

class CanvasWidget(QWidget):
    HANDLE_SIZE = 10

    def __init__(self, user_id=None, session_id=None):
        super().__init__()
        self.user_id = user_id or str(uuid.uuid4())
        self.session_id = session_id or str(uuid.uuid4())
        self.shapes = []
        self.drawing_mode = "square"
        self.current_color = "#000000"
        self.current_text = "texto"
        self.current_font_size = 14
        self.default_shape_size = 40
        self.selected_shape_index = None
        self.drag_offset = None
        self.resizing = False
        self.resizing_handle = None
        self.setStyleSheet("background-color: white; border-radius: 12px; padding: 8px;")

        supabase = get_supabase_client()
        try:
            supabase.table("whiteboard_sessions").insert({
                "id": self.session_id,
                "name": "Sessão automática via PySide"
            }).execute()
            print("✅ Sessão registrada no Supabase.")
        except Exception as e:
            print("⚠ Erro ao registrar sessão:", e)
        self.timer = QTimer()
        self.timer.timeout.connect(self.carregar_formas_do_supabase())
        self.timer.start(3000)
        

    def mousePressEvent(self, event):
        x, y = event.position().x(), event.position().y()
        if self.selected_shape_index is not None:
            handle = self.get_handle_at_pos(x, y)
            if handle is not None:
                self.resizing = True
                self.resizing_handle = handle
                return
        clicked_index = self.get_shape_at_pos(x, y)
        if clicked_index is not None:
            self.selected_shape_index = clicked_index
            shape = self.shapes[clicked_index]
            self.drag_offset = (x - shape["x"], y - shape["y"])
            self.update()
        else:
            self.selected_shape_index = None
            self.drag_offset = None
            shape_data = {
                "type": self.drawing_mode,
                "x": x,
                "y": y,
                "width": self.default_shape_size,
                "height": self.default_shape_size,
                "color": self.current_color,
                "text": self.current_text if self.drawing_mode == "text" else None,
                "font_size": self.current_font_size if self.drawing_mode == "text" else None,
            }
            self.shapes.append(shape_data)
            self.update()

    def mouseMoveEvent(self, event):
        x, y = event.position().x(), event.position().y()
        if self.resizing and self.selected_shape_index is not None:
            shape = self.shapes[self.selected_shape_index]
            cx, cy = shape["x"], shape["y"]
            width = shape.get("width", self.default_shape_size)
            height = shape.get("height", self.default_shape_size)
            half_w, half_h = width / 2, height / 2
            min_size = 10
            # Calcular novo tamanho mantendo proporção 1:1
            if self.resizing_handle == "br":  # bottom-right
                dx = x - (cx - half_w)
                dy = y - (cy - half_h)
                new_size = max(min_size, max(dx, dy))
                shape["width"] = new_size
                shape["height"] = new_size
            elif self.resizing_handle == "tr":  # top-right
                dx = x - (cx - half_w)
                dy = (cy + half_h) - y
                new_size = max(min_size, max(dx, dy))
                shape["width"] = new_size
                shape["height"] = new_size
                shape["y"] = cy + (y - (cy - half_h)) / 2
            elif self.resizing_handle == "bl":  # bottom-left
                dx = (cx + half_w) - x
                dy = y - (cy - half_h)
                new_size = max(min_size, max(dx, dy))
                shape["width"] = new_size
                shape["height"] = new_size
                shape["x"] = cx + (x - (cx - half_w)) / 2
            elif self.resizing_handle == "tl":  # top-left
                dx = (cx + half_w) - x
                dy = (cy + half_h) - y
                new_size = max(min_size, max(dx, dy))
                shape["width"] = new_size
                shape["height"] = new_size
                shape["x"] = cx + (x - (cx - half_w)) / 2
                shape["y"] = cy + (y - (cy - half_h)) / 2
            self.update()
        elif self.selected_shape_index is not None and self.drag_offset is not None and event.buttons() & Qt.LeftButton:
            dx, dy = self.drag_offset
            self.shapes[self.selected_shape_index]["x"] = x - dx
            self.shapes[self.selected_shape_index]["y"] = y - dy
            self.update()

    '''def mouseReleaseEvent(self, event):
        self.drag_offset = None
        self.resizing = False
        self.resizing_handle = None'''
    
    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        self.resizing = False
        self.resizing_handle = None
        self.salvar_formas_no_supabase()

    def get_shape_at_pos(self, x, y):
        for i in range(len(self.shapes)-1, -1, -1):
            shape = self.shapes[i]
            sx, sy = shape["x"], shape["y"]
            w, h = shape.get("width", self.default_shape_size), shape.get("height", self.default_shape_size)
            half_w, half_h = w/2, h/2
            if shape["type"] in ("square", "circle", "text"):
                if (sx - half_w <= x <= sx + half_w) and (sy - half_h <= y <= sy + half_h):
                    return i
            elif shape["type"] == "triangle":
                if (sx - half_w <= x <= sx + half_w) and (sy - half_h <= y <= sy + half_h):
                    return i
        return None

    def get_handle_at_pos(self, x, y):
        if self.selected_shape_index is None:
            return None
        shape = self.shapes[self.selected_shape_index]
        cx, cy = shape["x"], shape["y"]
        width = shape.get("width", self.default_shape_size)
        height = shape.get("height", self.default_shape_size)
        half_w, half_h = width / 2, height / 2
        handles = {
            "tl": (cx - half_w, cy - half_h),
            "tr": (cx + half_w, cy - half_h),
            "bl": (cx - half_w, cy + half_h),
            "br": (cx + half_w, cy + half_h),
        }
        for key, (hx, hy) in handles.items():
            if abs(x - hx) <= self.HANDLE_SIZE and abs(y - hy) <= self.HANDLE_SIZE:
                return key
        return None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for idx, shape in enumerate(self.shapes):
            t = shape.get("type")
            x = shape.get("x", 0)
            y = shape.get("y", 0)
            width = shape.get("width", self.default_shape_size)
            height = shape.get("height", self.default_shape_size)
            color = shape.get("color", "#000000")
            text = shape.get("text")
            font_size = shape.get("font_size", 14)
            if idx == self.selected_shape_index:
                painter.setPen(QPen(QColor("#6366F1"), 3, Qt.DashLine))
            else:
                painter.setPen(QPen(QColor(color), 2))
            painter.setBrush(QColor(color))
            half_width = width / 2
            half_height = height / 2
            if t == "square":
                painter.drawRoundedRect(x - half_width, y - half_height, width, height, 6, 6)
            elif t == "circle":
                painter.drawEllipse(x - half_width, y - half_height, width, height)
            elif t == "triangle":
                points = [
                    QPointF(x, y - half_height * 0.8),
                    QPointF(x - half_width, y + half_height * 0.8),
                    QPointF(x + half_width, y + half_height * 0.8)
                ]
                painter.drawPolygon(QPolygonF(points))
            elif t == "text" and text:
                font = QFont()
                font.setPointSize(font_size)
                painter.setFont(font)
                painter.drawText(x, y, text)
            # Desenhar alças de redimensionamento se selecionado
            if idx == self.selected_shape_index:
                self.draw_resize_handles(painter, x, y, width, height)

    def draw_resize_handles(self, painter, x, y, width, height):
        half_w = width / 2
        half_h = height / 2
        handle_color = QColor("#6366F1")
        for hx, hy in [
            (x - half_w, y - half_h),  # top-left
            (x + half_w, y - half_h),  # top-right
            (x - half_w, y + half_h),  # bottom-left
            (x + half_w, y + half_h),  # bottom-right
        ]:
            painter.setBrush(handle_color)
            painter.setPen(QPen(handle_color, 1))
            painter.drawRect(QRectF(hx - self.HANDLE_SIZE/2, hy - self.HANDLE_SIZE/2, self.HANDLE_SIZE, self.HANDLE_SIZE))

    def set_mode(self, mode):
        self.drawing_mode = mode

    def set_color(self, color):
        if self.selected_shape_index is not None:
            self.shapes[self.selected_shape_index]["color"] = color
            self.update()
        else:
            self.current_color = color

    def set_text(self, text):
        self.current_text = text

    def set_font_size(self, size):
        try:
            self.current_font_size = int(size)
        except ValueError:
            self.current_font_size = 14

    def clear_canvas(self):
        self.shapes.clear()
        self.selected_shape_index = None
        self.update()

    def load_shapes(self, shapes_data):
        if isinstance(shapes_data, list):
            self.shapes = shapes_data
            self.update()
        else:
            print("Erro: load_shapes recebeu dados inválidos.")
            self.shapes = []
            self.update()

    def delete_selected_shape(self):
        if self.selected_shape_index is not None:
            del self.shapes[self.selected_shape_index]
            self.selected_shape_index = None
            self.update()

    def change_selected_shape_size(self, factor):
        if self.selected_shape_index is not None:
            shape = self.shapes[self.selected_shape_index]
            shape["width"] = max(10, shape.get("width", self.default_shape_size) * factor)
            shape["height"] = max(10, shape.get("height", self.default_shape_size) * factor)
            self.update()

    def set_selected_shape_size(self, value):
        if self.selected_shape_index is not None:
            shape = self.shapes[self.selected_shape_index]
            shape["width"] = value
            shape["height"] = value
            self.update()

    def salvar_formas_no_supabase(self):
        supabase = get_supabase_client()
        if not self.shapes:
            return
        for shape in self.shapes:
            dados = {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "type": shape.get("type"),
                "x": shape.get("x"),
                "y": shape.get("y"),
                "width": shape.get("width"),
                "height": shape.get("height"),
                "color": shape.get("color"),
                "text": shape.get("text"),
                "font_size": shape.get("font_size"),
            }
            try:
                resposta = supabase.table("whiteboard_shapes").insert(dados).execute()
                print("✅ Forma salva:", resposta.data)
            except Exception as e:
                print("❌ Erro ao salvar no Supabase:", e)

    def carregar_formas_do_supabase(self):
        supabase = get_supabase_client()
        try:
            resposta = supabase.table("whiteboard_shapes").select("*").eq("session_id", self.session_id).execute()
            if resposta and hasattr(resposta, "data") and isinstance(resposta.data, list):
                self.shapes = resposta.data
                self.update()
                print(f"✅ {len(self.shapes)} formas carregadas do Supabase.")
            else:
                print("⚠ Nenhuma forma encontrada.")
        except Exception as e:
            print("❌ Erro ao carregar formas:", e)


    

