# -*- coding: utf-8 -*-
"""Tela de Login e Registro."""

from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QMessageBox, QFrame, QSizePolicy, QSpacerItem, QHBoxLayout, QToolButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from client.services import auth
from client.ui.main_window import MainWindow

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

class RegisterScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cadastro - Quadro Branco Colaborativo")
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)
        self.setStyleSheet("""
            QWidget {
                background-color: #F3F4F6;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)
        title = QLabel("Criar nova conta")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #222; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addSpacing(30)
        layout.addWidget(title, alignment=Qt.AlignHCenter)
        layout.addSpacing(10)
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 18px;
                padding: 32px 32px 24px 32px;
                box-shadow: 0 8px 32px rgba(60,60,100,0.10);
                border: none;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(18)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        card.setMaximumWidth(380)
        card.setMinimumWidth(280)
        layout.addStretch(1)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Seu email")
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 14px;
                border: none;
                border-radius: 10px;
                background: #F3F4F6;
                font-size: 16px;
                color: #222;
                margin-bottom: 12px;
            }
            QLineEdit:focus {
                background: #E0E7FF;
                outline: 2px solid #6366F1;
            }
        """)
        self.email_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card_layout.addWidget(self.email_input)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Sua senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 14px;
                border: none;
                border-radius: 10px;
                background: #F3F4F6;
                font-size: 16px;
                color: #222;
                margin-bottom: 12px;
            }
            QLineEdit:focus {
                background: #E0E7FF;
                outline: 2px solid #6366F1;
            }
        """)
        self.password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card_layout.addWidget(self.password_input)
        self.register_button = QPushButton("Cadastrar")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #6366F1;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 14px;
                font-size: 17px;
                font-weight: bold;
                margin-top: 18px;
                box-shadow: 0 2px 8px rgba(99,102,241,0.10);
            }
            QPushButton:hover {
                background-color: #4F46E5;
            }
        """)
        self.register_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.register_button.clicked.connect(self.handle_register)
        card_layout.addWidget(self.register_button)
        self.back_button = QPushButton("Já tem uma conta? Entrar")
        self.back_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #6366F1;
                font-size: 14px;
                text-decoration: underline;
                border: none;
                margin-top: 18px;
            }
            QPushButton:hover {
                color: #4F46E5;
            }
        """)
        self.back_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.back_button.clicked.connect(self.back_to_login)
        card_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)
        layout.addWidget(card, alignment=Qt.AlignHCenter)
        layout.addStretch(2)

    def handle_register(self):
        email = self.email_input.text()
        password = self.password_input.text()
        if not email or not password:
            show_messagebox(self, QMessageBox.Warning, "Campos Vazios", "Por favor, preencha email e senha para se cadastrar.")
            return
        if auth.signup(email, password):
            show_messagebox(self, QMessageBox.Information, "Cadastro realizado", "Conta criada com sucesso! Faça login para continuar.")
            self.back_to_login()

    def back_to_login(self):
        from client.ui.login_screen import LoginScreen
        self.login_screen = LoginScreen()
        self.login_screen.show()
        self.close()

class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Quadro Branco Colaborativo")
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)
        self.setStyleSheet("""
            QWidget {
                background-color: #F3F4F6;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)
        title = QLabel("Quadro Branco Colaborativo")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #222; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addSpacing(30)
        layout.addWidget(title, alignment=Qt.AlignHCenter)
        layout.addSpacing(10)
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 18px;
                padding: 32px 32px 24px 32px;
                box-shadow: 0 8px 32px rgba(60,60,100,0.10);
                border: none;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(18)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        card.setMaximumWidth(380)
        card.setMinimumWidth(280)
        layout.addStretch(1)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Seu email")
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 14px;
                border: none;
                border-radius: 10px;
                background: #F3F4F6;
                font-size: 16px;
                color: #222;
                margin-bottom: 12px;
            }
            QLineEdit:focus {
                background: #E0E7FF;
                outline: 2px solid #6366F1;
            }
        """)
        self.email_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card_layout.addWidget(self.email_input)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Sua senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 14px;
                border: none;
                border-radius: 10px;
                background: #F3F4F6;
                font-size: 16px;
                color: #222;
                margin-bottom: 12px;
            }
            QLineEdit:focus {
                background: #E0E7FF;
                outline: 2px solid #6366F1;
            }
        """)
        self.password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card_layout.addWidget(self.password_input)
        self.login_button = QPushButton("Entrar")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #6366F1;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 14px;
                font-size: 17px;
                font-weight: bold;
                margin-top: 18px;
                box-shadow: 0 2px 8px rgba(99,102,241,0.10);
            }
            QPushButton:hover {
                background-color: #4F46E5;
            }
        """)
        self.login_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.login_button.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_button)
        self.register_button = QPushButton("Não tem uma conta? Cadastre-se")
        self.register_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #6366F1;
                font-size: 14px;
                text-decoration: underline;
                border: none;
                margin-top: 18px;
            }
            QPushButton:hover {
                color: #4F46E5;
            }
        """)
        self.register_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.register_button.clicked.connect(self.open_register_screen)
        card_layout.addWidget(self.register_button, alignment=Qt.AlignCenter)
        layout.addWidget(card, alignment=Qt.AlignHCenter)
        layout.addStretch(2)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        if not email or not password:
            show_messagebox(self, QMessageBox.Warning, "Campos Vazios", "Por favor, preencha email e senha.")
            return
        if auth.login(email, password):
            current_user = auth.get_current_user()
            if current_user:
                self.main_window = MainWindow(user_id=current_user.id, email=email)
                self.main_window.show()
                self.close()
            else:
                show_messagebox(self, QMessageBox.Critical, "Erro", "Falha ao obter informações do usuário após login.")

    def open_register_screen(self):
        self.register_screen = RegisterScreen()
        self.register_screen.show()
        self.close()


