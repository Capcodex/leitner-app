import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QLineEdit, QTextEdit, QComboBox, QMessageBox, QFrame, QHBoxLayout, QScrollArea
from PySide6.QtGui import QIcon
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer
from LeitnerService import LeitnerService
from functools import partial
from datetime import datetime, timedelta



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
        """Interface pour afficher toutes les cartes avec une UI améliorée et défilement vertical."""
        self.clear_layout()

        # Création d'un conteneur pour le défilement
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Conteneur pour le contenu à faire défiler
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        all_cards = self.leitner_service.get_all_cards()

        if not all_cards:
            empty_label = QLabel("Aucune carte n'a été trouvée.")
            empty_label.setAlignment(Qt.AlignCenter)
            scroll_layout.addWidget(empty_label)
        else:
            for card in all_cards:
                # Créer un conteneur pour chaque carte
                card_frame = QFrame()
                card_frame.setFrameShape(QFrame.StyledPanel)
                card_frame.setStyleSheet("background-color: #f9f9f9; border-radius: 8px; padding: 10px; margin-bottom: 10px;")

                card_layout = QVBoxLayout()

                # Titre de la carte (question)
                card_label = QLabel(f"📋 {card['question']} (Boîte {card['box'] + 1})")
                card_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
                card_layout.addWidget(card_label)

                # Ligne horizontale pour les boutons d'action
                action_layout = QHBoxLayout()

                # Bouton Supprimer avec icône
                btn_delete = QPushButton("Supprimer")
                btn_delete.setIcon(QIcon("icons/trash.png"))  # Assurez-vous d'avoir une icône appropriée
                btn_delete.setStyleSheet("color: white; background-color: #e74c3c; border-radius: 4px; padding: 5px;")
                btn_delete.clicked.connect(partial(self.delete_card, card['question']))
                action_layout.addWidget(btn_delete)

                # Bouton Déplacer avec menu déroulant pour sélectionner la boîte
                btn_move = QPushButton("Déplacer")
                btn_move.setIcon(QIcon("icons/move.png"))  # Assurez-vous d'avoir une icône appropriée
                btn_move.setStyleSheet("color: white; background-color: #3498db; border-radius: 4px; padding: 5px;")
                combo_box = QComboBox()
                combo_box.addItems([f"Boîte {i + 1}" for i in range(5)])
                action_layout.addWidget(combo_box)

                btn_move.clicked.connect(partial(self.move_card, card['question'], combo_box))
                action_layout.addWidget(btn_move)

                # Ajouter le layout d'action à la carte
                card_layout.addLayout(action_layout)
                card_frame.setLayout(card_layout)
                
                # Ajouter le cadre de la carte au layout principal
                scroll_layout.addWidget(card_frame)

        # Configurer le widget de défilement
        scroll_area.setWidget(scroll_content)

        # Bouton de retour
        btn_back = QPushButton("Retour")
        btn_back.setStyleSheet("background-color: #2ecc71; color: white; border-radius: 4px; padding: 10px; margin-top: 10px;")
        btn_back.clicked.connect(self.init_home)
        scroll_layout.addWidget(btn_back)

        # Mise en place du layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)  # Ajoutez la zone de défilement au layout principal
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Bouton de retour
        btn_back = QPushButton("Retour")
        btn_back.setStyleSheet("background-color: #2ecc71; color: white; border-radius: 4px; padding: 10px;")
        btn_back.clicked.connect(self.init_home)
        layout.addWidget(btn_back)

        # Mise en place du layout principal
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def delete_card(self, question):
        """Supprime une carte."""
        self.leitner_service.delete_card(question)
        QMessageBox.information(self, "Supprimé", f"La carte '{question}' a été supprimée.")
        self.init_view_cards()

    def get_next_revision_time(box):
        """Renvoie la durée jusqu'à la prochaine révision en fonction de la boîte."""
        now = datetime.now()
        
        if box == 0:
            return now + timedelta(minutes=10)  # Boîte 1: 10 minutes
        elif box == 1:
            return now + timedelta(days=1)  # Boîte 2: 1 jour
        elif box == 2:
            return now + timedelta(weeks=1)  # Boîte 3: 1 semaine
        elif box == 3:
            return now + timedelta(weeks=4)  # Boîte 4: 1 mois (approximatif)
        elif box == 4:
            return now + timedelta(weeks=26)  # Boîte 5: 6 mois
        else:
            return now

    def move_card(self, question, combo_box):
        """Déplace une carte vers une autre boîte et met à jour la date de révision."""
        target_box = combo_box.currentIndex()
        self.leitner_service.move_card(question, target_box)
        
        # Ajouter la date de prochaine révision
        card = self.leitner_service.get_card_by_question(question)
        card['next_revision'] = get_next_revision_time(target_box)
        self.leitner_service.update_card(card)

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


    def init_revision_boxes(self):
        """Interface pour choisir une boîte de révision avec un décompte."""
        self.clear_layout()

        layout = QVBoxLayout()

        for i in range(5):  # Pour chaque boîte de 1 à 5
            cards_in_box = self.leitner_service.get_cards_by_box(i)

            if not cards_in_box:
                revision_status = "Pas de cartes à réviser"
            else:
                # Initialiser 'last_revision' pour les cartes qui ne l'ont pas encore
                for card in cards_in_box:
                    if 'last_revision' not in card:
                        card['last_revision'] = datetime.now().isoformat()  # Initialiser à la date actuelle

                # Trouver la date de révision la plus ancienne
                last_revision = min([card['last_revision'] for card in cards_in_box])  
                due, next_revision = self.is_revision_due(last_revision, i)

                if due:
                    revision_status = "Révision à faire"
                else:
                    time_left = next_revision - datetime.now()
                    revision_status = f"Prochaine révision dans {time_left}"

            btn_box = QPushButton(f"Boîte {i + 1} - {revision_status}")
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
        """Vérifie la réponse et met à jour la carte après révision."""
        user_command = self.command_input.toPlainText().strip()
        correct = user_command == current_card['command'].strip()

        if 'box' not in current_card:
            current_card['box'] = 0  # Initialisation dans la boîte 1

        # Met à jour la boîte en fonction de la réussite ou de l'échec
        if correct:
            current_card['box'] = min(current_card['box'] + 1, 4)  # Passe à la boîte suivante (max boîte 5)
        else:
            current_card['box'] = max(current_card['box'] - 1, 0)  # Revient à la boîte précédente

        current_card['last_revision'] = datetime.now().isoformat()  # Met à jour la date de révision
        self.leitner_service.update_card(current_card)

        self.results.append((current_card['question'], correct))
        self.current_index += 1  # Passe à la carte suivante

        if self.current_index < len(self.questions):
            self.show_current_question()
        else:
            self.show_results()

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

