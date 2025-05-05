# -*- coding: utf-8 -*-
"""Janela Principal do Quadro Branco Colaborativo (Redesenhada)."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QColorDialog, QLabel, QSizePolicy, QMessageBox,
    QFrame, QSpacerItem
)
from PySide6.QtGui import QIcon, QFont # Adicionado QFont
from PySide6.QtCore import Qt, QSize # Adicionado QSize

from client.ui.canvas_widget import CanvasWidget
from client.services.session_manager import get_session_shapes
from client.services.auth import logout, get_current_user

# Cores do Design (aproximadas da imagem)
COLOR_BACKGROUND = "#F3F4F6" # Um cinza bem claro, quase branco
COLOR_PRIMARY = "#4F46E5" # Roxo/Azul principal
COLOR_PRIMARY_HOVER = "#6366F1"
COLOR_DANGER = "#EF4444" # Vermelho para Limpar
COLOR_DANGER_HOVER = "#F87171"
COLOR_SECONDARY_BUTTON = "#FFFFFF"
COLOR_SECONDARY_BORDER = "#D1D5DB"
COLOR_TEXT_DARK = "#1F2937"
COLOR_TEXT_LIGHT = "#6B7280"
COLOR_CARD_BACKGROUND = "#FFFFFF"

class MainWindow(QMainWindow):
    def __init__(self, user_id, session_id):
        super().__init__()
        self.user_id = user_id
        self.session_id = session_id
        self.setWindowTitle("Quadro Branco Colaborativo") # Título genérico
        self.setMinimumSize(1000, 700)
        # Estilo geral da janela
        self.setStyleSheet(f"background-color: {COLOR_BACKGROUND}; font-family: Arial;")

        # Container principal
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setSpacing(15) # Espaçamento entre cards
        main_layout.setContentsMargins(25, 25, 25, 25)

        # --- Card Header --- 
        header_card = QFrame()
        header_card.setObjectName("HeaderCard")
        header_card.setStyleSheet(f"""
            #HeaderCard {{ 
                background-color: {COLOR_CARD_BACKGROUND};
                border-radius: 8px;
                padding: 10px 20px;
            }}
        """)
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Quadro Branco Colaborativo")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR_PRIMARY};")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Botão Colaborar (Placeholder)
        self.collab_button = QPushButton(" Colaborar") # Ícone pode ser adicionado depois
        # self.collab_button.setIcon(QIcon("path/to/collab_icon.png")) # Exemplo
        self.collab_button.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {COLOR_SECONDARY_BUTTON};
                color: {COLOR_TEXT_DARK};
                border: 1px solid {COLOR_SECONDARY_BORDER};
                padding: 8px 15px;
                border-radius: 6px;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #F9FAFB; }}
        """)
        # self.collab_button.clicked.connect(self.handle_collab) # Conectar função depois
        header_layout.addWidget(self.collab_button)

        # Botão Sair (Logout)
        self.logout_button = QPushButton(" Sair") # Ícone pode ser adicionado depois
        # self.logout_button.setIcon(QIcon("path/to/logout_icon.png")) # Exemplo
        self.logout_button.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {COLOR_SECONDARY_BUTTON};
                color: {COLOR_TEXT_DARK};
                border: 1px solid {COLOR_SECONDARY_BORDER};
                padding: 8px 15px;
                border-radius: 6px;
                font-size: 13px;
                margin-left: 10px; /* Espaço entre botões */
            }}
            QPushButton:hover {{ background-color: #F9FAFB; }}
        """)
        self.logout_button.clicked.connect(self.handle_logout)
        header_layout.addWidget(self.logout_button)

        main_layout.addWidget(header_card)

        # --- Card Toolbar --- 
        toolbar_card = QFrame()
        toolbar_card.setObjectName("ToolbarCard")
        toolbar_card.setStyleSheet(f"""
            #ToolbarCard {{ 
                background-color: {COLOR_CARD_BACKGROUND};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        toolbar_layout = QHBoxLayout(toolbar_card)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(10)

        self.mode_buttons = {}
        # Usando ícones Unicode simples por enquanto
        shape_icons = {"square": "□", "circle": "○", "triangle": "△", "text": "T"}
        for mode, icon in shape_icons.items():
            btn = QPushButton(icon)
            btn.setFixedSize(40, 40)
            btn.setCheckable(True)
            btn.setFont(QFont("Arial", 14))
            btn.setStyleSheet(f"""
                QPushButton {{ 
                    background-color: {COLOR_SECONDARY_BUTTON};
                    color: {COLOR_TEXT_DARK};
                    border: 1px solid {COLOR_SECONDARY_BORDER};
                    border-radius: 6px;
                }}
                QPushButton:checked {{ 
                    background-color: {COLOR_PRIMARY};
                    color: white;
                    border: 1px solid {COLOR_PRIMARY};
                }}
                QPushButton:hover {{ 
                    border-color: {COLOR_PRIMARY};
                }}
            """)
            # Usar lambda para capturar o modo correto
            btn.clicked.connect(lambda checked, m=mode: self.set_mode(m) if checked else None)
            toolbar_layout.addWidget(btn)
            self.mode_buttons[mode] = btn

        toolbar_layout.addStretch(1) # Empurra o botão Limpar para a direita

        # Botão Limpar
        clear_btn = QPushButton(" Limpar") # Ícone pode ser adicionado
        # clear_btn.setIcon(QIcon("path/to/trash_icon.png"))
        clear_btn.setFixedHeight(40)
        clear_btn.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {COLOR_DANGER};
                color: white;
                border: none;
                padding: 0px 20px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLOR_DANGER_HOVER}; }}
        """)
        clear_btn.clicked.connect(self.confirm_clear_canvas)
        toolbar_layout.addWidget(clear_btn)

        main_layout.addWidget(toolbar_card)

        # --- Card Controles (Cor, Texto) --- 
        controls_card = QFrame()
        controls_card.setObjectName("ControlsCard")
        controls_card.setStyleSheet(f"""
            #ControlsCard {{ 
                background-color: {COLOR_CARD_BACKGROUND};
                border-radius: 8px;
                padding: 15px;
            }}
            QLabel {{ color: {COLOR_TEXT_DARK}; font-size: 13px; }}
            QLineEdit {{ 
                border: 1px solid {COLOR_SECONDARY_BORDER};
                border-radius: 6px;
                padding: 5px 10px;
                background-color: white;
                color: {COLOR_TEXT_DARK};
            }}
        """)
        controls_layout = QHBoxLayout(controls_card)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(15)
        controls_layout.setAlignment(Qt.AlignLeft) # Alinha itens à esquerda

        # Botão de Excluir (Placeholder - funcionalidade não implementada)
        delete_shape_btn = QPushButton("") # Ícone Lixeira
        # delete_shape_btn.setIcon(QIcon("path/to/small_trash_icon.png"))
        delete_shape_btn.setFixedSize(32, 32)
        delete_shape_btn.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {COLOR_SECONDARY_BUTTON};
                border: 1px solid {COLOR_SECONDARY_BORDER};
                border-radius: 6px;
            }}
             QPushButton:hover {{ background-color: #F9FAFB; }}
        """)
        # delete_shape_btn.clicked.connect(self.delete_selected_shape) # Conectar depois
        controls_layout.addWidget(delete_shape_btn)

        controls_layout.addWidget(QLabel("Cor:"))
        self.color_button = QPushButton()
        self.color_button.setFixedSize(30, 30)
        # Cor inicial preta
        self.color_button.setStyleSheet(f"background-color: black; border: 1px solid {COLOR_SECONDARY_BORDER}; border-radius: 4px;")
        self.color_button.clicked.connect(self.choose_color)
        controls_layout.addWidget(self.color_button)

        controls_layout.addWidget(QLabel("Texto:"))
        self.text_input = QLineEdit("texto")
        self.text_input.setFixedWidth(250)
        self.text_input.textChanged.connect(self.update_canvas_text)
        controls_layout.addWidget(self.text_input)

        # Adicionar controle de tamanho da fonte (opcional, mas na tabela shapes)
        controls_layout.addWidget(QLabel("Tam. Fonte:"))
        self.font_size_input = QLineEdit("14")
        self.font_size_input.setFixedWidth(50)
        self.font_size_input.textChanged.connect(self.update_canvas_font_size)
        controls_layout.addWidget(self.font_size_input)

        controls_layout.addStretch() # Empurra tudo para a esquerda

        main_layout.addWidget(controls_card)

        # --- Card Canvas --- 
        canvas_card = QFrame()
        canvas_card.setObjectName("CanvasCard")
        # Define uma política de expansão vertical
        canvas_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas_card.setStyleSheet(f"""
            #CanvasCard {{ 
                background-color: {COLOR_CARD_BACKGROUND};
                border-radius: 8px;
                padding: 1px; /* Pequena borda interna */
            }}
        """)
        canvas_layout = QVBoxLayout(canvas_card)
        canvas_layout.setContentsMargins(10, 10, 10, 10) # Padding interno para o canvas

        self.canvas = CanvasWidget(user_id=self.user_id, session_id=self.session_id)
        # Canvas deve expandir para preencher o card
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setStyleSheet(f"background-color: white; border-radius: 6px;") # Estilo do canvas interno
        canvas_layout.addWidget(self.canvas)

        main_layout.addWidget(canvas_card)

        # --- Mensagem Flutuante (Placeholder) --- 
        # Implementar isso corretamente exigiria um widget sobreposto ou status bar
        # Por ora, apenas um QLabel no final
        # status_label = QLabel("Quadro branco pronto! Selecione uma forma para começar a desenhar.")
        # status_label.setStyleSheet(f"background-color: {COLOR_CARD_BACKGROUND}; color: {COLOR_TEXT_DARK}; border-radius: 6px; padding: 8px 12px; border: 1px solid {COLOR_SECONDARY_BORDER};")
        # status_label.setAlignment(Qt.AlignCenter)
        # main_layout.addWidget(status_label, 0, Qt.AlignBottom | Qt.AlignRight)
        # main_layout.addStretch() # Para empurrar para baixo? Testar.

        self.setCentralWidget(main_container)
        self.set_mode("square")  # modo inicial
        self.load_initial_shapes() # Carrega formas existentes

    def set_mode(self, mode):
        # Garante que apenas um botão de modo esteja checado
        for m, btn in self.mode_buttons.items():
            if m != mode:
                btn.setChecked(False)
        self.canvas.set_mode(mode)
        print(f"Modo alterado para: {mode}")

    def choose_color(self):
        # Usa a cor atual do canvas como cor inicial do diálogo
        initial_color = QColor(self.canvas.current_color)
        color = QColorDialog.getColor(initial_color, self)
        if color.isValid():
            color_name = color.name()
            self.canvas.set_color(color_name)
            self.color_button.setStyleSheet(f"background-color: {color_name}; border: 1px solid {COLOR_SECONDARY_BORDER}; border-radius: 4px;")
            print(f"Cor alterada para: {color_name}")

    def update_canvas_text(self):
        self.canvas.set_text(self.text_input.text())

    def update_canvas_font_size(self):
        self.canvas.set_font_size(self.font_size_input.text())

    def load_initial_shapes(self):
        print(f"Carregando formas para a sessão {self.session_id}...")
        shapes_data = get_session_shapes(self.session_id)
        if shapes_data:
            self.canvas.load_shapes(shapes_data)
            print(f"{len(shapes_data)} formas carregadas.")
        else:
            # Não mostra erro se apenas não houver formas
            print("Nenhuma forma encontrada para esta sessão.")

    def confirm_clear_canvas(self):
        reply = QMessageBox.question(self, "Confirmar Limpeza",
                                     "Tem certeza que deseja limpar todo o canvas? Esta ação (ainda) não pode ser desfeita no banco de dados.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.canvas.clear_canvas()

    def handle_logout(self):
        if logout():
            print("Logout realizado. Fechando aplicação.")
            self.close()
            # Para voltar à tela de login, precisaríamos de uma lógica diferente
            # no run.py ou em um gerenciador de janelas.
        else:
            QMessageBox.warning(self, "Erro de Logout", "Não foi possível deslogar.")

    # def handle_collab(self):
    #     # Lógica para o botão Colaborar (ex: mostrar lista de usuários, convidar)
    #     print("Botão Colaborar clicado - funcionalidade a implementar.")
    #     QMessageBox.information(self, "Colaborar", "Funcionalidade de colaboração ainda não implementada.")

    def closeEvent(self, event):
        if get_current_user():
            logout()
        event.accept()

