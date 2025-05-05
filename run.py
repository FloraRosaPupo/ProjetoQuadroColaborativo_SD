from client.ui.login_screen import LoginScreen
from PySide6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginScreen()  # ✅ Corrigido aqui
    login.show()
    sys.exit(app.exec())
