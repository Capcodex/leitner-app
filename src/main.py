import sys
from PySide6.QtWidgets import QApplication
from .model import LeitnerService
from .views.home_view import HomeView

class LeitnerApp(HomeView):
    def __init__(self):
        super().__init__()
        self.leitner_service = LeitnerService()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LeitnerApp()
    window.show()
    sys.exit(app.exec())
