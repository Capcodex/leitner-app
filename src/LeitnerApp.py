import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QLineEdit, QTextEdit, QComboBox, QMessageBox, QGroupBox, QFrame
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from LeitnerService import LeitnerService
from functools import partial

class LeitnerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Leitner App")
        self.setGeometry(100, 100, 800, 600)

        self.leitner_service = LeitnerService()
        self.questions = []  # Liste des questions dans une boîte spécifique
        self.current_index = 0  # Index de la fiche en cours dans la liste
        self.results = []  # Stocke les résultats des réponses

        self.init_home()

    def init_home(self):
        """Initialisation de l'interface d'accueil."""
        self.clear_layout()

        layout = QVBoxLayout()

        # Création des boutons principaux
        btn_add_card = QPushButton("Enregistrer une nouvelle fiche")
        btn_add_card.clicked.connect(self.init_add_card)
        btn_add_card.setStyleSheet("background-color: #5c85d6; color: white; padding: 10px; font-size: 18px; border-radius: 5px;")

        btn_revision = QPushButton("Révisions")
        btn_revision.clicked.connect(self.init_revision_boxes)
        btn_revision.setStyleSheet("background-color: #5c85d6; color: white; padding: 10px; font-size: 18px; border-radius: 5px;")

        btn_view_cards = QPushButton("Voir toutes les cartes")
        btn_view_cards.clicked.connect(self.init_view_cards)
        btn_view_cards.setStyleSheet("background-color: #5c85d6; color: white; padding: 10px; font-size: 18px; border-radius: 5px;")

        layout.addWidget(btn_add_card)
        layout.addWidget(btn_revision)
        layout.addWidget(btn_view_cards)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def init_view_cards(self):
        """Interface pour afficher toutes les cartes."""
        self.clear_layout()

        layout = QVBoxLayout()

        all_cards = self.leitner_service.get_all_cards()

        for card in all_cards:
            card_label = QLabel(f"{card['question']} (Boîte {card['box'] + 1})")
            layout.addWidget(card_label)

            btn_delete = QPushButton("Supprimer")
            btn_delete.clicked.connect(partial(self.delete_card, card['question']))
            layout.addWidget(btn_delete)

            btn_move = QPushButton("Déplacer vers la boîte")
            combo_box = QComboBox()
            combo_box.addItems([f"Boîte {i + 1}" for i in range(5)])
            layout.addWidget(combo_box)
            btn_move.clicked.connect(partial(self.move_card, card['question'], combo_box))
            layout.addWidget(btn_move)

        btn_back = QPushButton("Retour")
        btn_back.clicked.connect(self.init_home)
        layout.addWidget(btn_back)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def delete_card(self, question):
        """Supprime une carte."""
        self.leitner_service.delete_card(question)
        QMessageBox.information(self, "Supprimé", f"La carte '{question}' a été supprimée.")
        self.init_view_cards()

    def move_card(self, question, combo_box):
        """Déplace une carte vers une autre boîte."""
        target_box = combo_box.currentIndex()
        self.leitner_service.move_card(question, target_box)
        QMessageBox.information(self, "Déplacé", f"La carte '{question}' a été déplacée vers la boîte {target_box + 1}.")
        self.init_view_cards()

    def init_add_card(self):
        """Interface pour ajouter une nouvelle fiche."""
        self.clear_layout()

        layout = QVBoxLayout()

        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Posez une question")
        self.question_input.setStyleSheet("font-size: 16px; padding: 8px;")

        self.command_input = QTextEdit()
        self.command_input.setPlaceholderText("Tapez la commande correspondante")
        self.command_input.setStyleSheet("font-size: 16px; padding: 8px;")

        btn_submit = QPushButton("Enregistrer")
        btn_submit.clicked.connect(self.submit_question)
        btn_submit.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")

        btn_back = QPushButton("Retour")
        btn_back.clicked.connect(self.init_home)
        btn_back.setStyleSheet("background-color: #d9534f; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")

        layout.addWidget(self.question_input)
        layout.addWidget(self.command_input)
        layout.addWidget(btn_submit)
        layout.addWidget(btn_back)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def submit_question(self):
        """Soumettre une nouvelle fiche et l'enregistrer dans la boîte 1."""
        question = self.question_input.text()
        command = self.command_input.toPlainText()
        if question and command:
            card = {
                'question': question,
                'command': command,
                'box': 0  # Par défaut, toutes les nouvelles cartes commencent dans la boîte 1 (index 0)
            }
            self.leitner_service.add_card(card)
            QMessageBox.information(self, "Enregistré", f"La carte '{question}' a été ajoutée.")
            self.init_home()


    def init_revision_boxes(self):
        """Interface pour choisir une boîte de révision."""
        self.clear_layout()

        layout = QVBoxLayout()

        for i in range(5):
            btn_box = QPushButton(f"Réviser la boîte {i + 1}")
            btn_box.clicked.connect(partial(self.start_revision, i))
            btn_box.setStyleSheet("background-color: #5c85d6; color: white; padding: 10px; font-size: 18px; border-radius: 5px;")
            layout.addWidget(btn_box)

        btn_back = QPushButton("Retour")
        btn_back.clicked.connect(self.init_home)
        btn_back.setStyleSheet("background-color: #d9534f; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")
        layout.addWidget(btn_back)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_revision(self, selected_box):
        """Commence la révision des fiches dans la boîte sélectionnée."""
        self.clear_layout()

        self.questions = self.leitner_service.get_cards_by_box(selected_box)
        self.results = []  # Réinitialise les résultats
        self.current_index = 0  # Réinitialise l'index des cartes

        if self.questions:
            self.show_current_question()
        else:
            self.no_more_cards()

    def show_current_question(self):
        """Affiche la fiche en cours."""
        layout = QVBoxLayout()

        if self.current_index < len(self.questions):
            current_card = self.questions[self.current_index]

            card_frame = QFrame()
            card_frame.setFrameShape(QFrame.StyledPanel)
            card_frame.setStyleSheet("border: 2px solid #5c85d6; padding: 15px; margin-bottom: 10px;")

            card_layout = QVBoxLayout()

            question_label = QLabel(current_card['question'])
            question_label.setFont(QFont("Arial", 16, QFont.Bold))
            question_label.setStyleSheet("color: #333;")
            card_layout.addWidget(question_label)

            self.command_input = QTextEdit()
            self.command_input.setPlaceholderText("Tapez la commande correspondant à la réponse")
            self.command_input.setStyleSheet("font-size: 14px; padding: 8px;")
            card_layout.addWidget(self.command_input)

            btn_submit = QPushButton("Soumettre")
            btn_submit.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; font-size: 14px; border-radius: 5px;")
            btn_submit.clicked.connect(partial(self.submit_revision, current_card))
            card_layout.addWidget(btn_submit)

            card_frame.setLayout(card_layout)
            layout.addWidget(card_frame)

        btn_finish = QPushButton("Terminer la révision")
        btn_finish.clicked.connect(self.show_results)
        btn_finish.setStyleSheet("background-color: #d9534f; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")
        layout.addWidget(btn_finish)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def submit_revision(self, current_card):
        """Vérifie la réponse pour la fiche courante et gère la logique Leitner."""
        user_command = self.command_input.toPlainText().strip()
        correct = user_command == current_card['command'].strip()

        # On s'assure que la carte a une boîte
        if 'box' not in current_card:
            current_card['box'] = 0  # Initialisation dans la boîte 1 (index 0)

        if correct:
            current_card['box'] = min(current_card['box'] + 1, 4)  # Passe à la boîte suivante (max boîte 5)
        else:
            current_card['box'] = max(current_card['box'] - 1, 0)  # Revient à la boîte précédente (min boîte 1)

        self.leitner_service.update_card(current_card)  # Met à jour la carte dans le système

        self.results.append((current_card['question'], correct))  # Stocke le résultat
        self.current_index += 1  # Passe à la carte suivante

        if self.current_index < len(self.questions):
            self.show_current_question()
        else:
            self.show_results()


    def show_results(self):
        """Affiche les résultats après la révision."""
        layout = QVBoxLayout()

        for question, correct in self.results:
            result_label = QLabel(f"{question}: {'Correct' if correct else 'Incorrect'}")
            result_label.setStyleSheet(f"font-size: 16px; color: {'green' if correct else 'red'};")
            layout.addWidget(result_label)

        btn_back = QPushButton("Retour à l'accueil")
        btn_back.clicked.connect(self.init_home)
        btn_back.setStyleSheet("background-color: #5c85d6; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")
        layout.addWidget(btn_back)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

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
