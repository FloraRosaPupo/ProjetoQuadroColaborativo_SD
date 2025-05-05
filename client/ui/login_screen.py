# -*- coding: utf-8 -*-
"""Tela de Login e Registro."""

from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QMessageBox, QFrame, QDialog, QListWidget, QListWidgetItem, QHBoxLayout,
    QInputDialog
)
from PySide6.QtCore import Qt
from client.services import auth
from client.ui.main_window import MainWindow
# Importa funções de gerenciamento de sessão
from client.services.session_manager import list_sessions, create_session

class SessionDialog(QDialog):
    """Diálogo para selecionar ou criar uma sessão."""
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.selected_session_id = None
        self.setWindowTitle("Selecionar ou Criar Sessão")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Sessões existentes:"))
        self.session_list = QListWidget()
        self.session_list.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.session_list)

        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Atualizar Lista")
        self.refresh_button.clicked.connect(self.populate_sessions)
        button_layout.addWidget(self.refresh_button)

        self.create_button = QPushButton("Criar Nova Sessão")
        self.create_button.clicked.connect(self.create_new_session)
        button_layout.addWidget(self.create_button)

        self.select_button = QPushButton("Entrar na Sessão")
        self.select_button.clicked.connect(self.accept_selection)
        self.select_button.setEnabled(False) # Habilita ao selecionar item
        button_layout.addWidget(self.select_button)

        layout.addLayout(button_layout)

        self.session_list.currentItemChanged.connect(
            lambda current, previous: self.select_button.setEnabled(current is not None)
        )

        self.populate_sessions()

    def populate_sessions(self):
        self.session_list.clear()
        sessions = list_sessions()
        if sessions:
            for session in sessions:
                item = QListWidgetItem(f"{session.get('name', 'Sessão sem nome')} (ID: ...{session.get('id', '')[-6:]})")
                # Armazena o ID completo no item data
                item.setData(Qt.UserRole, session.get('id'))
                self.session_list.addItem(item)
        else:
            self.session_list.addItem("Nenhuma sessão encontrada.")

    def create_new_session(self):
        session_name, ok = QInputDialog.getText(self, "Criar Sessão", "Nome da nova sessão:")
        if ok and session_name:
            new_session = create_session(self.user_id, session_name)
            if new_session:
                self.selected_session_id = new_session.get('id')
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível criar a sessão.")
        elif ok:
             QMessageBox.warning(self, "Nome Inválido", "O nome da sessão não pode estar vazio.")

    def accept_selection(self):
        current_item = self.session_list.currentItem()
        if current_item and current_item.data(Qt.UserRole):
            self.selected_session_id = current_item.data(Qt.UserRole)
            self.accept()
        else:
            QMessageBox.warning(self, "Seleção Inválida", "Por favor, selecione uma sessão válida da lista ou crie uma nova.")

class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Entrar ou Cadastrar")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #EEF2FF; font-family: Arial;")
        self.main_window = None # Para manter referência

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Card
        card = QFrame()
        card.setFixedSize(420, 350) # Aumentado para caber botão de cadastro
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 40px 30px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        card_layout.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(QLabel("Bem-vindo!"))

        # Inputs
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFixedHeight(40)
        self.email_input.setStyleSheet("QLineEdit { border: 1px solid #ccc; border-radius: 6px; padding-left: 10px; background: #fff; color: #000; }")
        card_layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.setStyleSheet("QLineEdit { border: 1px solid #ccc; border-radius: 6px; padding-left: 10px; background: #fff; color: #000; }")
        card_layout.addWidget(self.password_input)

        # Botões
        self.login_button = QPushButton("Entrar")
        self.login_button.setFixedHeight(40)
        self.login_button.setStyleSheet("QPushButton { background-color: #4F46E5; color: white; font-weight: bold; font-size: 14px; border-radius: 6px; } QPushButton:hover { background-color: #5F57F6; }")
        self.login_button.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_button)

        self.register_button = QPushButton("Não tem uma conta? Cadastre-se")
        self.register_button.setStyleSheet("QPushButton { background: transparent; color: #4F46E5; font-size: 12px; text-decoration: underline; border: none; }")
        self.register_button.clicked.connect(self.handle_signup_request)
        card_layout.addWidget(self.register_button, alignment=Qt.AlignCenter)

        layout.addWidget(card)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        if not email or not password:
            QMessageBox.warning(self, "Campos Vazios", "Por favor, preencha email e senha.")
            return

        if auth.login(email, password):
            current_user = auth.get_current_user()
            if current_user:
                self.open_session_dialog(current_user.id)
            else:
                 QMessageBox.critical(self, "Erro", "Falha ao obter informações do usuário após login.")
        # A função auth.login já mostra a mensagem de erro específica
        # else:
        #     # Mensagem genérica já é mostrada por auth.login em caso de falha
        #     pass

    def handle_signup_request(self):
        email = self.email_input.text()
        password = self.password_input.text()
        if not email or not password:
            QMessageBox.warning(self, "Campos Vazios", "Por favor, preencha email e senha para se cadastrar.")
            return

        # Chama a função de signup do módulo auth
        auth.signup(email, password)
        # A função signup já mostra mensagens de sucesso/erro

    def open_session_dialog(self, user_id):
        dialog = SessionDialog(user_id, self)
        if dialog.exec() == QDialog.Accepted and dialog.selected_session_id:
            session_id = dialog.selected_session_id
            print(f"Entrando na sessão: {session_id}")
            # Passa user_id e session_id para a MainWindow
            self.main_window = MainWindow(user_id=user_id, session_id=session_id)
            self.main_window.show()
            self.close() # Fecha a tela de login
        else:
            print("Seleção de sessão cancelada ou falhou.")
            # Opcional: Deslogar o usuário se a seleção for obrigatória
            # auth.logout()


