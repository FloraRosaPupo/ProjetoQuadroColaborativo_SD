# -*- coding: utf-8 -*-
"""Widget de Canvas para desenho colaborativo."""

from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPolygonF
from PySide6.QtCore import Qt, QPointF

# Importa o cliente Supabase
from client.services.supabase_client import get_supabase_client, supabase

# Define o nome correto da tabela
SHAPES_TABLE = "whiteboard_shapes"

class CanvasWidget(QWidget):
    def __init__(self, user_id=None, session_id=None): # Adicionado session_id
        super().__init__()
        self.user_id = user_id # Será preenchido após login
        self.session_id = session_id # Será preenchido ao entrar/criar sessão
        self.shapes = []
        self.drawing_mode = "square"
        self.current_color = "#000000" # Renomeado de self.color para evitar conflito
        self.current_text = "texto" # Renomeado de self.text
        self.current_font_size = 14 # Adicionado para corresponder à tabela
        self.default_shape_size = 40 # Tamanho padrão para formas

        # Estilo inicial, será sobrescrito pelo MainWindow no redesign
        self.setStyleSheet("background-color: white; border-radius: 12px; padding: 8px;")
        self.supabase_client = None
        try:
            self.supabase_client = get_supabase_client()
        except ConnectionError as e:
            print(f"Erro ao obter cliente Supabase: {e}")
            # Opcional: Mostrar um erro para o usuário
            # QMessageBox.critical(self, "Erro de Conexão", "Não foi possível conectar ao banco de dados.")

    def mousePressEvent(self, event):
        if not self.supabase_client or not self.session_id or not self.user_id:
            msg = "Não é possível desenhar: "
            if not self.supabase_client: msg += "Cliente Supabase não disponível. "
            if not self.session_id: msg += "ID da sessão não definido. "
            if not self.user_id: msg += "ID do usuário não definido. "
            print(msg)
            QMessageBox.warning(self, "Erro", msg)
            return

        x, y = event.position().x(), event.position().y()

        # Dados a serem salvos no Supabase e usados localmente
        shape_data = {
            "session_id": self.session_id,
            "user_id": str(self.user_id), # Garante UUID como string
            "type": self.drawing_mode,
            "x": x,
            "y": y,
            "width": self.default_shape_size, # Adicionado - valor padrão
            "height": self.default_shape_size, # Adicionado - valor padrão
            "color": self.current_color,
            "text": self.current_text if self.drawing_mode == "text" else None,
            "font_size": self.current_font_size if self.drawing_mode == "text" else None, # Adicionado
        }

        # Adiciona localmente para renderização imediata
        # Faz uma cópia para evitar problemas se a inserção falhar e removermos depois
        local_shape = shape_data.copy()
        self.shapes.append(local_shape)
        self.update()

        # Tenta salvar no Supabase
        try:
            # Usa o nome correto da tabela
            response = self.supabase_client.table(SHAPES_TABLE).insert(shape_data).execute()

            # Verifica se houve erro na resposta da API
            if hasattr(response, 'error') and response.error:
                raise Exception(response.error.message)
            # print("Forma salva no Supabase:", response.data)

        except Exception as e:
            print(f"Erro ao salvar forma no Supabase: {e}")
            # Remove a forma localmente se falhar ao salvar
            if local_shape in self.shapes:
                self.shapes.remove(local_shape)
            self.update()
            QMessageBox.warning(self, "Erro de Salvamento", f"Não foi possível salvar a forma no banco de dados.\nErro: {e}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for shape in self.shapes:
            # Usa .get() com padrões para segurança
            t = shape.get("type", "square")
            x = shape.get("x", 0)
            y = shape.get("y", 0)
            color = shape.get("color", "#000000")
            text_content = shape.get("text")
            font_size = shape.get("font_size", 14)
            # Usa width/height se disponíveis, senão usa padrão
            width = shape.get("width", self.default_shape_size)
            height = shape.get("height", self.default_shape_size)
            half_width = width / 2
            half_height = height / 2

            if t == "text" and text_content:
                painter.setPen(QColor(color)) # Usa a cor definida para o texto
                font = QFont("Arial", font_size)
                painter.setFont(font)
                # Desenha o texto a partir do ponto clicado (x, y)
                painter.drawText(QPointF(x, y), text_content)
                continue

            pen = QPen(QColor(color))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(QColor(color))

            if t == "square":
                # Usa width/height para desenhar o retângulo centrado em x, y
                painter.drawRoundedRect(x - half_width, y - half_height, width, height, 6, 6)
            elif t == "circle":
                # Usa width/height para desenhar a elipse centrada em x, y
                painter.drawEllipse(x - half_width, y - half_height, width, height)
            elif t == "triangle":
                # Ajusta pontos baseados em half_width e half_height
                points = [
                    QPointF(x, y - half_height * 0.8), # Ponto superior
                    QPointF(x - half_width, y + half_height * 0.8), # Inferior esquerdo
                    QPointF(x + half_width, y + half_height * 0.8)  # Inferior direito
                ]
                painter.drawPolygon(QPolygonF(points))

    def set_mode(self, mode):
        self.drawing_mode = mode

    def set_color(self, color):
        self.current_color = color

    def set_text(self, text):
        self.current_text = text

    def set_font_size(self, size):
        try:
            self.current_font_size = int(size)
        except ValueError:
            self.current_font_size = 14 # Padrão se a conversão falhar

    def clear_canvas(self):
        # TODO: Implementar exclusão no Supabase (requer lógica de sessão/permissão)
        # Exemplo: self.supabase_client.table(SHAPES_TABLE).delete().eq('session_id', self.session_id).execute()
        print("Limpeza do canvas local. Exclusão no Supabase não implementada.")
        self.shapes.clear()
        self.update()

    def load_shapes(self, shapes_data):
        """Carrega formas (por exemplo, do Supabase ao entrar na sessão)."""
        # Valida se shapes_data é uma lista antes de atribuir
        if isinstance(shapes_data, list):
            self.shapes = shapes_data
            self.update()
        else:
            print("Erro: load_shapes recebeu dados inválidos.")
            self.shapes = [] # Garante que self.shapes seja sempre uma lista
            self.update()

