# -*- coding: utf-8 -*-
"""Ponto de entrada da aplicação cliente (MODIFICADO PARA VISUALIZAÇÃO)."""

from PySide6.QtWidgets import QApplication
import sys

# Importa a MainWindow diretamente
from client.ui.main_window import MainWindow
# from client.ui.login_screen import LoginScreen # Comentado para visualização

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # --- MODIFICAÇÃO PARA VISUALIZAÇÃO --- 
    # Abre a MainWindow diretamente com IDs falsos, pulando login e seleção de sessão.
    # ATENÇÃO: Isso é apenas para visualização do layout.
    # Nenhuma funcionalidade de salvar, carregar ou colaborar funcionará.
    print("AVISO: Executando em modo de visualização direta da MainWindow.")
    print("Funcionalidades de login, sessão e Supabase estão desabilitadas.")
    main_win = MainWindow(user_id="VISUALIZACAO", session_id="VISUALIZACAO")
    main_win.show()
    # --- FIM DA MODIFICAÇÃO ---

    # # Fluxo original com login:
    # login = LoginScreen()
    # login.show()

    sys.exit(app.exec())

