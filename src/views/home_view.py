from PySide6.QtWidgets import QVBoxLayout, QPushButton, QWidget # type: ignore
from .add_card_view import AddCardView
from .review_view import ReviewView
from .card_management_view import CardManagementView

class HomeView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_home()

    def init_home(self):
        """Initialisation de l'interface d'accueil."""
        layout = QVBoxLayout()
        self.setWindowTitle("Leitner App")
        self.setGeometry(100, 100, 800, 600)

        # Création des boutons principaux
        btn_add_card = QPushButton("Enregistrer une nouvelle fiche")
        btn_add_card.clicked.connect(self.init_add_card)
        btn_add_card.setStyleSheet("background-color: #5c85d6; color: white; padding: 10px; font-size: 18px; border-radius: 5px;")

        btn_revision = QPushButton("Commencer la révision")
        btn_revision.clicked.connect(self.init_review_view)
        btn_revision.setStyleSheet("background-color: #5c85d6; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")

        btn_manage_cards = QPushButton("Gestion des fiches")
        btn_manage_cards.setStyleSheet("background-color: #5c85d6; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")
        btn_manage_cards.clicked.connect(self.init_view_cards)


        layout.addWidget(btn_add_card)
        layout.addWidget(btn_revision)
        layout.addWidget(btn_manage_cards)

        container = QWidget()
        container.setLayout(layout)
        self.setLayout(layout)

    def init_add_card(self):
        """Ouvre l'interface pour ajouter une nouvelle fiche."""
        self.add_card_view = AddCardView()
        self.add_card_view.show()

    def init_review_view(self):
        """Ouvre l'interface de révision des fiches."""
        self.review_view = ReviewView()
        self.review_view.show()
        
    def init_view_cards(self):
        """Ouvre l'interface de révision des fiches."""
        self.review_view = CardManagementView()
        self.review_view.show()