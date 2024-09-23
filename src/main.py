import sys
from PySide6.QtWidgets import QApplication
from LeitnerApp import LeitnerApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LeitnerApp()
    window.show()  # Assurez-vous que cela est bien là
    sys.exit(app.exec())
