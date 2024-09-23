import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QLineEdit, QTextEdit
from LeitnerService import LeitnerService
from functools import partial  # Utilisé pour capturer correctement la valeur de la boîte

class LeitnerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Leitner App")
        self.setGeometry(100, 100, 800, 600)

        self.leitner_service = LeitnerService()
        self.current_card_index = 0  # Pour suivre la carte actuelle dans la révision
        self.questions = []  # Liste des questions dans une boîte spécifique

        self.init_home()

    def init_home(self):
        """Initialisation de l'interface d'accueil."""
        self.clear_layout()

        layout = QVBoxLayout()

        btn_add_card = QPushButton("Enregistrer une nouvelle fiche")
        btn_add_card.clicked.connect(self.init_add_card)

        btn_revision = QPushButton("Révisions")
        btn_revision.clicked.connect(self.init_revision_boxes)

        layout.addWidget(btn_add_card)
        layout.addWidget(btn_revision)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def init_add_card(self):
        """Interface pour ajouter une nouvelle fiche."""
        self.clear_layout()

        layout = QVBoxLayout()

        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Posez une question")
        layout.addWidget(self.question_input)

        self.command_input = QTextEdit()
        self.command_input.setPlaceholderText("Tapez la commande correspondante")
        layout.addWidget(self.command_input)

        btn_submit = QPushButton("Enregistrer")
        btn_submit.clicked.connect(self.submit_question)
        layout.addWidget(btn_submit)

        btn_back = QPushButton("Retour")
        btn_back.clicked.connect(self.init_home)
        layout.addWidget(btn_back)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def submit_question(self):
        """Soumettre une nouvelle fiche et l'enregistrer dans la boîte 1."""
        question = self.question_input.text()
        command = self.command_input.toPlainText()
        if question and command:
            self.leitner_service.add_card(question, command)
            self.init_home()

    def init_revision_boxes(self):
        """Interface pour choisir une boîte de révision."""
        self.clear_layout()

        layout = QVBoxLayout()

        for i in range(5):
            btn_box = QPushButton(f"Réviser la boîte {i + 1}")
            # Utilisation de functools.partial pour capturer la valeur de i
            btn_box.clicked.connect(partial(self.start_revision, i))
            layout.addWidget(btn_box)

        btn_back = QPushButton("Retour")
        btn_back.clicked.connect(self.init_home)
        layout.addWidget(btn_back)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_revision(self, selected_box):
        """Commence la révision des fiches dans la boîte sélectionnée."""
        self.clear_layout()

        self.questions = self.leitner_service.get_cards_by_box(selected_box)
        self.current_card_index = 0  # Réinitialiser à la première fiche

        if self.questions:
            self.show_current_question()
        else:
            self.no_more_cards()

    def show_current_question(self):
        """Affiche la fiche courante à réviser."""
        if self.current_card_index < len(self.questions):
            layout = QVBoxLayout()

            current_card = self.questions[self.current_card_index]
            self.question_label = QLabel(current_card['question'])
            layout.addWidget(self.question_label)

            self.command_input = QTextEdit()
            self.command_input.setPlaceholderText("Tapez la commande correspondant à la réponse")
            layout.addWidget(self.command_input)

            btn_submit = QPushButton("Soumettre")
            btn_submit.clicked.connect(self.submit_revision)
            layout.addWidget(btn_submit)

            btn_back = QPushButton("Retour")
            btn_back.clicked.connect(self.init_home)
            layout.addWidget(btn_back)

            container = QWidget()
            container.setLayout(layout)
            self.setCentralWidget(container)
        else:
            self.no_more_cards()

    def submit_revision(self):
        """Vérifie la réponse et passe à la fiche suivante."""
        current_card = self.questions[self.current_card_index]
        user_command = self.command_input.toPlainText()

        correct = user_command.strip() == current_card['command'].strip()

        self.leitner_service.revise_card(current_card['question'], correct)

        # Afficher le résultat avant de passer à la question suivante
        result_text = "Bonne réponse" if correct else "Mauvaise réponse"
        self.show_result(result_text)

    def show_result(self, result_text):
        """Affiche le résultat (bonne ou mauvaise réponse) avant de passer à la fiche suivante."""
        layout = QVBoxLayout()

        result_label = QLabel(result_text)
        layout.addWidget(result_label)

        btn_next = QPushButton("Suivant")
        btn_next.clicked.connect(self.next_question)
        layout.addWidget(btn_next)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def next_question(self):
        """Passe à la fiche suivante dans la révision."""
        self.current_card_index += 1
        self.show_current_question()

    def no_more_cards(self):
        """Affiche un message quand il n'y a plus de fiches à réviser."""
        layout = QVBoxLayout()

        label = QLabel("Il n'y a plus de fiches à réviser dans cette boîte.")
        layout.addWidget(label)

        btn_back = QPushButton("Retour")
        btn_back.clicked.connect(self.init_home)
        layout.addWidget(btn_back)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def clear_layout(self):
        """Nettoie l'interface avant de charger un nouveau layout."""
        if self.centralWidget():
            self.centralWidget().setParent(None)

# main.py
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = LeitnerApp()
    window.show()

    sys.exit(app.exec())
