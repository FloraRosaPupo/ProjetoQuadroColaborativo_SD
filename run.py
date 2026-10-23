import sys
from PySide6.QtWidgets import QApplication
from client.ui.login_screen import LoginScreen
from ws_client import start_ws_client

if __name__ == "__main__":
    app = QApplication(sys.argv)
    worker = start_ws_client()
    app.aboutToQuit.connect(worker.stop)
    login = LoginScreen()
    login.show()
    try:
        sys.exit(app.exec())
    finally:
        worker.stop()
