# -*- coding: utf-8 -*-
"""Janela Principal do Quadro Branco Colaborativo."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QColorDialog, QLabel, QSizePolicy, QMessageBox,
    QFrame, QSpacerItem, QSpinBox
)
from PySide6.QtGui import QIcon, QFont, QColor
from PySide6.QtCore import Qt, QSize

from client.ui.canvas_widget import CanvasWidget
from client.services.auth import logout, get_current_user
from client.services.supabase_client import get_supabase_client

# Cores do Design
COLOR_BACKGROUND = "#F3F4F6"
COLOR_PRIMARY = "#4F46E5"
COLOR_PRIMARY_HOVER = "#6366F1"
COLOR_DANGER = "#EF4444"
COLOR_DANGER_HOVER = "#F87171"
COLOR_SECONDARY_BUTTON = "#FFFFFF"
COLOR_SECONDARY_BORDER = "#D1D5DB"
COLOR_TEXT_DARK = "#1F2937"
COLOR_TEXT_LIGHT = "#6B7280"
COLOR_CARD_BACKGROUND = "#FFFFFF"

class MainWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Quadro Branco Colaborativo")
        self.setMinimumSize(900, 650)
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {COLOR_BACKGROUND};
            }}
        """)

        # Barra superior alinhada à direita, espaçamento adequado
        top_info_bar = QWidget()
        top_info_bar.setFixedHeight(50)
        top_info_layout = QHBoxLayout(top_info_bar)
        top_info_layout.setContentsMargins(0, 0, 24, 0)
        top_info_layout.setSpacing(18)
        top_info_layout.addStretch(1)
        user = get_current_user()
        email_label = QLabel(user.email if user and hasattr(user, 'email') else "Usuário")
        email_label.setStyleSheet("font-size: 14px; color: #222; font-weight: 500;")
        top_info_layout.addWidget(email_label)
        people_label = QLabel("Pessoas na sessão: 5")
        people_label.setStyleSheet("font-size: 14px; color: #6366F1; font-weight: 500; margin-left: 18px;")
        top_info_layout.addWidget(people_label)
        logout_button = QPushButton("Sair")
        logout_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_SECONDARY_BUTTON};
                color: {COLOR_TEXT_DARK};
                border: 1.2px solid {COLOR_SECONDARY_BORDER};
                border-radius: 7px;
                padding: 4px 14px;
                font-size: 14px;
                font-weight: 500;
                margin-left: 18px;
            }}
            QPushButton:hover {{
                background-color: #F0F7FF;
                border-color: {COLOR_PRIMARY};
            }}
        """)
        logout_button.clicked.connect(self.handle_logout)
        top_info_layout.addWidget(logout_button)

        # Layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 18, 30, 18)
        layout.setSpacing(12)
        layout.addWidget(top_info_bar)

        # Card da barra de ferramentas centralizado e compacto
        top_bar = QFrame()
        top_bar.setFixedHeight(100)
        top_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_CARD_BACKGROUND};
                border-radius: 18px;
                padding: 14px 18px 10px 18px;
                border: 1.5px solid #E5E7EB;
                box-shadow: 0 4px 24px rgba(0,0,0,0.08);
                max-width: 2000px;
                margin-left: auto;
                margin-right: auto;
            }}
        """)
        top_bar.setMaximumWidth(2000)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(8, 8, 8, 8)
        top_layout.setSpacing(12)

        # Botões de modo
        self.mode_buttons = {}
        modes = {
            "square": "Quadrado",
            "circle": "Círculo",
            "triangle": "Triângulo",
            "text": "Texto"
        }
        for mode, label in modes.items():
            btn = QPushButton(label)
            btn.setMinimumWidth(110)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_SECONDARY_BUTTON};
                    color: {COLOR_TEXT_DARK};
                    border: 1.5px solid {COLOR_SECONDARY_BORDER};
                    border-radius: 8px;
                    padding: 10px 22px;
                    font-size: 15px;
                    font-weight: 500;
                    transition: background 0.2s;
                }}
                QPushButton:hover {{
                    background-color: #F0F7FF;
                    border-color: {COLOR_PRIMARY};
                }}
                QPushButton:checked {{
                    background-color: {COLOR_PRIMARY};
                    color: white;
                    border-color: {COLOR_PRIMARY};
                }}
            """)
            btn.clicked.connect(lambda checked, m=mode: self.set_mode(m))
            self.mode_buttons[mode] = btn
            top_layout.addWidget(btn)

        # Área de cor com rótulo
        color_label = QLabel("Cor:")
        color_label.setStyleSheet("font-size: 15px; color: #222; font-weight: 500; margin-left: 8px;")
        top_layout.addWidget(color_label)
        self.color_button = QPushButton()
        self.color_button.setFixedSize(40, 40)
        self.color_button.setStyleSheet(f"background-color: #000000; border: 1.5px solid {COLOR_SECONDARY_BORDER}; border-radius: 8px;")
        self.color_button.clicked.connect(self.choose_color)
        top_layout.addWidget(self.color_button)

        # Input de texto
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Digite o texto...")
        self.text_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px;
                border: 1.5px solid {COLOR_SECONDARY_BORDER};
                border-radius: 8px;
                font-size: 15px;
                background: #fff;
                color: {COLOR_TEXT_DARK};
            }}
            QLineEdit:focus {{
                border: 1.5px solid {COLOR_PRIMARY};
                background: #F0F7FF;
            }}
        """)
        self.text_input.textChanged.connect(self.update_canvas_text)
        top_layout.addWidget(self.text_input)

        # Botão de limpar
        clear_button = QPushButton("Limpar")
        clear_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #F87171;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 22px;
                font-size: 15px;
                font-weight: bold;
                margin-left: 8px;
            }}
            QPushButton:hover {{
                background-color: #EF4444;
            }}
        """)
        clear_button.clicked.connect(self.confirm_clear_canvas)
        top_layout.addWidget(clear_button)

        # Botão de excluir forma selecionada
        delete_button = QPushButton("Excluir")
        delete_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #F3F4F6;
                color: #BDBDBD;
                border: none;
                border-radius: 8px;
                padding: 10px 22px;
                font-size: 15px;
                font-weight: bold;
                margin-left: 8px;
            }}
            QPushButton:enabled {{
                background-color: #FBBF24;
                color: #222;
            }}
            QPushButton:hover:enabled {{
                background-color: #F59E42;
            }}
        """)
        delete_button.clicked.connect(self.delete_selected_shape)
        top_layout.addWidget(delete_button)
        self.delete_button = delete_button

        layout.addWidget(top_bar, alignment=Qt.AlignHCenter)

        # Canvas
        self.canvas = CanvasWidget(user_id=self.user_id)
        self.canvas.setStyleSheet(f"background-color: #fff; border-radius: 16px; border: 1.5px solid #E5E7EB;")
        layout.addWidget(self.canvas)

        # Configuração inicial
        self.set_mode("square")
        self.update_delete_button_state()
        self.canvas.mousePressEvent = self.wrap_mouse_press(self.canvas.mousePressEvent)

    def set_mode(self, mode):
        for m, btn in self.mode_buttons.items():
            if m != mode:
                btn.setChecked(False)
        self.canvas.set_mode(mode)
        print(f"Modo alterado para: {mode}")

    def choose_color(self):
        dialog = QColorDialog(self)
        dialog.setOption(QColorDialog.DontUseNativeDialog, True)  # Força modo não nativo
        dialog.setCurrentColor(QColor(self.canvas.current_color))
        dialog.setStyleSheet("""
            QWidget {
                background-color: #fff;
                color: #222;
                font-size: 15px;
            }
            QLabel, QLineEdit {
                color: #222;
            }
            QPushButton {
                color: #222;
                background-color: #F3F4F6;
                border-radius: 6px;
                padding: 6px 16px;
            }
            QPushButton:disabled {
                color: #aaa;
            }
        """)
        if dialog.exec() == QColorDialog.Accepted:
            color = dialog.selectedColor()
            if color.isValid():
                color_name = color.name()
                self.canvas.set_color(color_name)
                self.color_button.setStyleSheet(f"background-color: {color_name}; border: 1.5px solid {COLOR_SECONDARY_BORDER}; border-radius: 8px;")
                print(f"Cor alterada para: {color_name}")

    def update_canvas_text(self):
        self.canvas.set_text(self.text_input.text())

    def confirm_clear_canvas(self):
        reply = show_messagebox(self, QMessageBox.Question, "Confirmar Limpeza",
                               "Tem certeza que deseja limpar todo o canvas?",
                               QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.canvas.clear_canvas()

    def handle_logout(self):
        supabase = get_supabase_client()
        reply = show_messagebox(self, QMessageBox.Question, "Confirmar Saída",
                               "Tem certeza que deseja sair?",
                               QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                # Deleta todas as formas dessa sessão
                supabase.table("whiteboard_shapes").delete().eq("session_id", self.canvas.session_id).execute()

                # Opcional: também remove o registro da sessão
                supabase.table("whiteboard_sessions").delete().eq("id", self.canvas.session_id).execute()

                print("✅ Dados apagados do Supabase.")
            except Exception as e:
                print("❌ Erro ao deletar dados:", e)
            logout()
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

    def delete_selected_shape(self):
        if self.canvas.selected_shape_index is not None:
            self.canvas.delete_selected_shape()
            self.update_delete_button_state()

    def update_delete_button_state(self):
        enabled = self.canvas.selected_shape_index is not None
        self.delete_button.setEnabled(enabled)

    def wrap_mouse_press(self, original_mouse_press):
        def new_mouse_press(event):
            original_mouse_press(event)
            self.update_delete_button_state()
        return new_mouse_press

# Função utilitária para QMessageBox estilizado

def show_messagebox(parent, icon, title, text, buttons=QMessageBox.Ok):
    msg = QMessageBox(parent)
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setStandardButtons(buttons)
    msg.setStyleSheet('''
        QMessageBox {
            background-color: #F3F4F6;
            color: #222;
            font-size: 15px;
        }
        QLabel {
            color: #222;
            font-size: 15px;
        }
        QPushButton {
            background-color: #6366F1;
            color: white;
            border-radius: 8px;
            padding: 8px 18px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #4F46E5;
        }
    ''')
    return msg.exec()

