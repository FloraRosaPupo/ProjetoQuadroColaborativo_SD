from client.ui.login_screen import LoginScreen
from PySide6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
<<<<<<< Updated upstream
=======
    start_ws_client() # 👈 e chama aqui antes de abrir a interface

>>>>>>> Stashed changes
    app = QApplication(sys.argv)
    login = LoginScreen()  # ✅ Corrigido aqui
    login.show()
    sys.exit(app.exec())
