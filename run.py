from client.ui.login_screen import LoginScreen
from PySide6.QtWidgets import QApplication
import sys

from ws_client import start_ws_client  # 👈 adiciona essa linha aqui

if __name__ == "__main__":
    start_ws_client()  # 👈 e chama aqui antes de abrir a interface

    app = QApplication(sys.argv)
    login = LoginScreen()
    login.show()
    sys.exit(app.exec())

