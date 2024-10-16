import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
                            QWidget, QLineEdit, QTextEdit, QComboBox, QMessageBox, QFrame, 
                            QHBoxLayout, QScrollArea, QInputDialog, QDialog)
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, QEvent
from src.model import LeitnerService
from functools import partial
from datetime import datetime, timedelta

class ReviewView(QWidget):
    def __init__(self):
        super().__init__()
        self.leitner_service = LeitnerService() 
        self.init_combined_view()

    def init_combined_view(self):
        """Interface combinée pour sélectionner une catégorie et choisir une boîte de révision."""

        layout = QVBoxLayout()

        # Menu déroulant pour sélectionner une catégorie
        self.category_input = QComboBox()
        self.category_input.setStyleSheet("font-size: 16px; padding: 8px;")
        self.category_input.setEditable(True)

        # Ajouter un placeholder
        self.category_input.addItem("Sélectionnez une catégorie")
        self.category_input.setItemData(0, 0, Qt.UserRole - 1)  # Empêche la sélection de l'élément 0

        # Charger les catégories existantes
        categories = self.leitner_service.get_all_categories()
        if categories:
            self.category_input.addItems(categories)

        # Connecter la modification de la catégorie pour actualiser les boîtes
        self.category_input.currentIndexChanged.connect(self.update_revision_boxes)

        # Zone pour les boutons de sélection de boîtes
        self.box_layout = QVBoxLayout()

        # Bouton de retour
        btn_back = QPushButton("Retour")
        btn_back.clicked.connect(self.close)
        btn_back.setStyleSheet("background-color: #d9534f; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")

        layout.addWidget(self.category_input)
        layout.addLayout(self.box_layout)  # Ajouter la zone des boîtes de révision
        layout.addWidget(btn_back)

        self.setLayout(layout)

    def update_revision_boxes(self):
        """Actualise l'affichage des boîtes de révision en fonction de la catégorie sélectionnée."""

        # Vider l'ancien contenu de la boîte
        for i in reversed(range(self.box_layout.count())): 
            widget_to_remove = self.box_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.deleteLater()

        selected_category = self.category_input.currentText()
        if selected_category == "Sélectionnez une catégorie":
            return  # Ne rien faire si aucune catégorie n'est sélectionnée

        # Ajouter les boutons de boîtes de révision filtrés par catégorie
        for i in range(5):  # Boîtes de 1 à 5
            cards_in_box = self.leitner_service.get_cards_by_box_and_category(i, selected_category)

            if not cards_in_box:
                revision_status = "Pas de cartes à réviser"
            else:
                last_revision = min([card['last_revision'] for card in cards_in_box])
                due, next_revision = self.is_revision_due(last_revision, i)
                revision_status = "Révision à faire" if due else f"Prochaine révision dans {self.format_time_left(next_revision - datetime.now())}"

            btn_box = QPushButton(f"Boîte {i + 1} - {revision_status}")
            btn_box.clicked.connect(partial(self.launch_start_review, i, selected_category))
            btn_box.setStyleSheet("background-color: #5c85d6; color: white; padding: 10px; font-size: 18px; border-radius: 5px;")
            self.box_layout.addWidget(btn_box)

    def launch_start_review(self, selected_box, selected_category):
        print(f"Launching review for box {selected_box} and category {selected_category}")
        self.start_review_view = StartReviewView(selected_box, selected_category)
        self.start_review_view.show()





    def is_revision_due(self, last_revision, box):
        """
        Vérifie si une révision est due pour une carte donnée, en fonction de l'intervalle de la boîte.
        
        last_revision : string (date ISO format)
        box : int (index de la boîte, entre 0 et 4)
        
        Renvoie un tuple (due, next_revision)
        due : booléen indiquant si la révision est due
        next_revision : datetime de la prochaine révision
        """
        last_revision_date = datetime.fromisoformat(last_revision)
        # Délais de révision en fonction de la boîte (en minutes, jours, semaines, mois)
        intervals = [
            timedelta(minutes=10),   # Boîte 1 : 10 minutes
            timedelta(days=1),       # Boîte 2 : 1 jour
            timedelta(weeks=1),      # Boîte 3 : 1 semaine
            timedelta(weeks=4),      # Boîte 4 : 1 mois (approximé à 4 semaines)
            timedelta(weeks=24)      # Boîte 5 : 6 mois (approximé à 24 semaines)
        ]
        
        # Calcul de la prochaine date de révision en fonction de la boîte
        next_revision = last_revision_date + intervals[box]
        
        # Si la date actuelle est supérieure ou égale à la prochaine révision, elle est due
        due = datetime.now() >= next_revision
        
        return due, next_revision
    
    def format_time_left(self, time_left):
        """Formate le temps restant pour l'affichage, en ajoutant des jours si nécessaire."""
        total_seconds = int(time_left.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        # Si les heures dépassent 24, on calcule le nombre de jours et d'heures restantes
        if hours >= 24:
            days, hours = divmod(hours, 24)
            return f"{days}j {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
        

class StartReviewView(QWidget):
    def __init__(self, selected_box, selected_category):
        super().__init__()
        self.leitner_service = LeitnerService()
        self.results = []
        self.current_index = 0
        self.selected_box = selected_box
        self.selected_category = selected_category
        self.questions = self.leitner_service.get_cards_by_box_and_category(selected_box, selected_category)

        self.init_ui()  # Initialiser l'interface une seule fois

        if self.questions:
            self.show_current_question()
        else:
            self.no_more_cards()

    def init_ui(self):
        """Initialise l'interface utilisateur de base."""
        self.layout = QVBoxLayout()

        # Cadre pour la carte
        self.card_frame = QFrame()
        self.card_frame.setFrameShape(QFrame.StyledPanel)
        self.card_frame.setStyleSheet("border: 2px solid #5c85d6; padding: 15px; margin-bottom: 10px;")
        self.card_layout = QVBoxLayout()

        # Label pour la question
        self.question_label = QLabel()
        self.question_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.question_label.setStyleSheet("color: #333;")
        self.card_layout.addWidget(self.question_label)

        # Champ texte pour la commande
        self.command_input = QTextEdit()
        self.command_input.setPlaceholderText("Tapez la commande correspondant à la réponse")
        self.command_input.setStyleSheet("font-size: 14px; padding: 8px;")
        self.card_layout.addWidget(self.command_input)

        # Bouton soumettre
        self.btn_submit = QPushButton("Soumettre")
        self.btn_submit.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; font-size: 14px; border-radius: 5px;")
        self.btn_submit.clicked.connect(self.submit_revision)
        self.card_layout.addWidget(self.btn_submit)

        self.command_input.installEventFilter(self)  # Connecter l'event filter pour 'Entrée'

        self.card_frame.setLayout(self.card_layout)
        self.layout.addWidget(self.card_frame)

        # Bouton terminer
        self.btn_finish = QPushButton("Terminer la révision")
        self.btn_finish.clicked.connect(self.show_results)
        self.btn_finish.setStyleSheet("background-color: #d9534f; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")
        self.layout.addWidget(self.btn_finish)

        self.setLayout(self.layout)

    def show_current_question(self):
        """Met à jour l'interface pour afficher la question actuelle sans recréer les widgets."""
        current_card = self.questions[self.current_index]
        self.question_label.setText(current_card['question'])  # Mettre à jour la question
        self.command_input.clear()  # Effacer le champ de texte pour la nouvelle réponse

    def submit_revision(self):
        """Soumet la réponse et passe à la carte suivante ou affiche les résultats."""
        current_card = self.questions[self.current_index]
        user_command = self.command_input.toPlainText().strip()
        correct_answer = current_card['command'].strip()

        correct = user_command == correct_answer

        # Met à jour la boîte en fonction de la réussite ou de l'échec
        if correct:
            current_card['box'] = min(current_card['box'] + 1, 4)  # Passe à la boîte suivante (max boîte 4)
        else:
            current_card['box'] = max(current_card['box'] - 1, 0)  # Revient à la boîte précédente

        current_card['last_revision'] = datetime.now().isoformat()  # Met à jour la date de révision
        self.leitner_service.update_card(current_card)  # Enregistre les modifications

        # Ajoute la question, la correction et la bonne réponse dans les résultats
        self.results.append((current_card['question'], correct, correct_answer))
        self.current_index += 1  # Passe à la carte suivante

        # Affiche la question suivante ou les résultats
        if self.current_index < len(self.questions):
            self.show_current_question()
        else:
            self.show_results()

    def eventFilter(self, source, event):
        """Intercepte les événements clavier pour activer la soumission avec la touche 'Entrée'."""
        if source == self.command_input and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                # Simule le clic sur le bouton "Soumettre"
                self.submit_revision()
                return True  # Indique que l'événement a été géré
        return super().eventFilter(source, event)

    def format_time_left(self, time_left):
        """Formate le temps restant pour l'affichage, en ajoutant des jours si nécessaire."""
        total_seconds = int(time_left.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        # Si les heures dépassent 24, on calcule le nombre de jours et d'heures restantes
        if hours >= 24:
            days, hours = divmod(hours, 24)
            return f"{days}j {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def no_more_cards(self):
        """Affiche un message quand il n'y a plus de fiches à réviser."""
        self.clear_layout()

        label = QLabel("Il n'y a plus de fiches à réviser dans cette boîte.")
        self.layout.addWidget(label)

        btn_back = QPushButton("Retour")
        btn_back.clicked.connect(self.close)
        self.layout.addWidget(btn_back)

    def show_results(self):
        """Affiche les résultats après la révision."""
        self.clear_layout()

        if not self.results:
            # S'il n'y a pas de résultats, on affiche un message
            label = QLabel("Aucun résultat à afficher.")
            self.layout.addWidget(label)
        else:
            # Affiche chaque résultat
            for question, correct, correct_answer in self.results:
                # Affichage personnalisé pour les réponses correctes et incorrectes
                if correct:
                    result_label = QLabel(f"✔ {question}: Correct!")
                    result_label.setStyleSheet("font-size: 18px; color: green;")
                else:
                    result_label = QLabel(f"✘ {question}: Incorrect! La bonne réponse est: {correct_answer}")
                    result_label.setStyleSheet("font-size: 18px; color: red;")

                self.layout.addWidget(result_label)

        btn_back = QPushButton("Retour à l'accueil")
        btn_back.clicked.connect(self.close)
        btn_back.setStyleSheet("background-color: #5c85d6; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")
        self.layout.addWidget(btn_back)

    def clear_layout(self):
        """Supprime tous les widgets du layout actuel."""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
