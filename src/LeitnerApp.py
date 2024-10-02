import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
                            QWidget, QLineEdit, QTextEdit, QComboBox, QMessageBox, QFrame, 
                            QHBoxLayout, QScrollArea, QInputDialog, QDialog)
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, QEvent
from LeitnerService import LeitnerService
from functools import partial
from datetime import datetime, timedelta



class LeitnerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.setWindowTitle("Leitner App")
        self.setGeometry(100, 100, 800, 600)

        self.leitner_service = LeitnerService()
        self.questions = []  # Liste des questions dans une boîte spécifique
        self.current_index = 0  # Index de la fiche en cours dans la liste
        self.results = []  # Stocke les résultats des réponses

        self.init_home()


# ---------------------------------- Partie 0 : Page d'accueil --------------------------------------
    def init_home(self):
        """Initialisation de l'interface d'accueil.
        Composé de 3 parties :
        1) Ajouter une nouvelle fiche
        2) Révision 
        3 Gestion de fiches
        """
        self.clear_layout()

        layout = QVBoxLayout()

        # Création des boutons principaux
        btn_add_card = QPushButton("Enregistrer une nouvelle fiche")
        btn_add_card.clicked.connect(self.init_add_card)
        btn_add_card.setStyleSheet("background-color: #5c85d6; color: white; padding: 10px; font-size: 18px; border-radius: 5px;")

        btn_revision = QPushButton("Commencer la révision")
        btn_revision.clicked.connect(self.init_category_selection)  # Appelle d'abord la sélection de catégorie
        btn_revision.setStyleSheet("background-color: #5c85d6; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")

        btn_view_cards = QPushButton("Voir toutes les fiches")
        btn_view_cards.clicked.connect(self.init_view_cards)
        btn_view_cards.setStyleSheet("background-color: #5c85d6; color: white; padding: 10px; font-size: 18px; border-radius: 5px;")

        layout.addWidget(btn_add_card)
        layout.addWidget(btn_revision)
        layout.addWidget(btn_view_cards)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

# ------------------------------- Partie 1 : Ajouter une nouvelle fiche -------------------------------------

    def init_add_card(self):
        """Interface pour ajouter une nouvelle fiche."""
        self.clear_layout()

        layout = QVBoxLayout()

        # Champ de question
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Posez une question")
        self.question_input.setStyleSheet("font-size: 16px; padding: 8px;")
        self.question_input.returnPressed.connect(self.submit_question)  # Appuyer sur Entrée soumet la question

        # Champ de commande (QTextEdit)
        self.command_input = QTextEdit()
        self.command_input.setPlaceholderText("Tapez la commande correspondante")
        self.command_input.setStyleSheet("font-size: 16px; padding: 8px;")

        # Champ de catégorie (QComboBox) avec placeholder
        self.category_input = QComboBox()
        self.category_input.addItem("Sélectionnez ou ajoutez une catégorie")
        self.category_input.addItems(self.leitner_service.categories)  # Charger les catégories existantes
        self.category_input.setEditable(True)  # Permettre à l'utilisateur d'ajouter une nouvelle catégorie
        self.category_input.setStyleSheet("font-size: 16px; padding: 8px;")

        # Bouton d'enregistrement
        btn_submit = QPushButton("Enregistrer")
        btn_submit.clicked.connect(self.submit_question)
        btn_submit.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")

        # Bouton de retour
        btn_back = QPushButton("Retour")
        btn_back.clicked.connect(self.init_home)
        btn_back.setStyleSheet("background-color: #d9534f; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")

        # Ajout des widgets au layout
        layout.addWidget(self.question_input)
        layout.addWidget(self.command_input)
        layout.addWidget(self.category_input)
        layout.addWidget(btn_submit)
        layout.addWidget(btn_back)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)



    def on_category_selected(self, index):
        """Modifier le style quand une catégorie est sélectionnée."""
        if index == 0:
            # Si le placeholder est sélectionné, rester en gris
            self.category_input.setStyleSheet("color: gray;")
        else:
            # Si une vraie catégorie est sélectionnée
            self.category_input.setStyleSheet("color: black;")




    def submit_question(self):
        """Soumettre une nouvelle fiche et l'enregistrer dans la boîte 1."""
        question = self.question_input.text()
        command = self.command_input.toPlainText()
        category = self.category_input.currentText()  # Récupérer la catégorie sélectionnée
        
        if question and command:
            # Enregistrer la catégorie si elle n'existe pas
            if category and category not in self.leitner_service.categories:
                self.leitner_service.add_category(category)

            # Enregistrer la carte
            card = {
                'question': question,
                'command': command,
                'box': 0,  # Par défaut, toutes les nouvelles cartes commencent dans la boîte 1 (index 0)
                'category': category  # Enregistrer la catégorie
            }
            self.leitner_service.add_card(card)
            QMessageBox.information(self, "Enregistré", f"La carte '{question}' a été ajoutée.")
            self.init_home()


# --------------------------------- Partie 2 : Révision des fiches ------------------------------------

    def init_category_selection(self):
        """Interface pour sélectionner une catégorie avant de commencer la révision."""
        self.clear_layout()

        layout = QVBoxLayout()

        # Menu déroulant pour sélectionner une catégorie (self.category_input pour la rendre accessible)
        self.category_input = QComboBox()  # Utilise self ici
        self.category_input.setStyleSheet("font-size: 16px; padding: 8px;")
        self.category_input.setEditable(True)

        # Ajouter un placeholder
        self.category_input.addItem("Sélectionnez une catégorie")
        self.category_input.setItemData(0, 0, Qt.UserRole - 1)  # Empêche la sélection de l'élément 0

        # Charger les catégories existantes
        categories = self.leitner_service.get_all_categories()
        if categories:
            self.category_input.addItems(categories)

        # Bouton pour valider la sélection de catégorie
        btn_select_category = QPushButton("Choisir cette catégorie")
        btn_select_category.clicked.connect(self.init_revision_boxes)  # Passe à la sélection des boîtes
        btn_select_category.setStyleSheet("background-color: #5c85d6; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")

        layout.addWidget(self.category_input)  # Ajoute le QComboBox au layout
        layout.addWidget(btn_select_category)

        btn_back = QPushButton("Retour")
        btn_back.clicked.connect(self.init_home)
        btn_back.setStyleSheet("background-color: #d9534f; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")
        layout.addWidget(btn_back)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


    def init_revision_boxes(self):
        """Interface pour choisir une boîte de révision avec un décompte."""
        # Sauvegarder la catégorie sélectionnée avant d'effacer le layout
        selected_category = self.category_input.currentText()

        # Maintenant, tu peux effacer le layout en toute sécurité
        self.clear_layout()

        layout = QVBoxLayout()

        # Filtrer les fiches par boîte et par catégorie
        for i in range(5):  # Pour chaque boîte de 1 à 5
            cards_in_box = self.leitner_service.get_cards_by_box_and_category(i, selected_category)

            if not cards_in_box:
                revision_status = "Pas de cartes à réviser"
                due = False  # Aucune révision due
                next_revision = None  # Pas de prochaine révision
            else:
                for card in cards_in_box:
                    if 'last_revision' not in card:
                        card['last_revision'] = datetime.now().isoformat()  # Initialiser à la date actuelle

                last_revision = min([card['last_revision'] for card in cards_in_box])
                due, next_revision = self.is_revision_due(last_revision, i)

                revision_status = "Révision à faire" if due else f"Prochaine révision dans {self.format_time_left(next_revision - datetime.now())}"

            btn_box = QPushButton(f"Boîte {i + 1} - {revision_status}")
            btn_box.clicked.connect(partial(self.start_revision, i, selected_category))
            btn_box.setStyleSheet("background-color: #5c85d6; color: white; padding: 10px; font-size: 18px; border-radius: 5px;")
            layout.addWidget(btn_box)

        btn_back = QPushButton("Retour")
        btn_back.clicked.connect(self.init_home)
        btn_back.setStyleSheet("background-color: #d9534f; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")
        layout.addWidget(btn_back)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)



    def start_revision(self, selected_box, selected_category):
        """Commence la révision des fiches dans la boîte et la catégorie sélectionnées."""
        self.clear_layout()

        # Filtrer les fiches par boîte et catégorie
        self.questions = self.leitner_service.get_cards_by_box_and_category(selected_box, selected_category)
        self.results = []  # Réinitialise les résultats
        self.current_index = 0  # Réinitialise l'index des cartes
        self.selected_box = selected_box  # Stocker la boîte actuelle pour la révision

        if self.questions:
            self.show_current_question()
        else:
            self.no_more_cards()


    def get_cards_by_box_and_category(self, box, category):
        """Renvoie les cartes filtrées par boîte et catégorie."""
        return [card for card in self.cards if card['box'] == box and card['category'] == category]

    def complete_revision(self):
        """Appelée lorsque la révision de la boîte est terminée."""
        # Mettre à jour 'last_revision' pour toutes les cartes révisées
        for card in self.questions:
            card['last_revision'] = datetime.now().isoformat()
            self.leitner_service.update_card(card)  # Sauvegarder les changements
        
        self.init_revision_boxes()

    def revise_card(self, card):
        """Met à jour la date de dernière révision après avoir révisé une carte."""
        card['last_revision'] = datetime.now().isoformat()
        # Vous pouvez aussi enregistrer cette information dans le service ou la base de données si nécessaire
        self.leitner_service.update_card(card)

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


        
    def show_current_question(self):
        """Affiche la fiche en cours avec un raccourci pour soumettre via la touche 'Entrée'."""
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
            btn_submit.clicked.connect(lambda: self.submit_revision(current_card))
            card_layout.addWidget(btn_submit)

            # Connecter la touche 'Entrée' à l'action de soumettre
            self.command_input.installEventFilter(self)

            card_frame.setLayout(card_layout)
            layout.addWidget(card_frame)

        btn_finish = QPushButton("Terminer la révision")
        btn_finish.clicked.connect(self.show_results)
        btn_finish.setStyleSheet("background-color: #d9534f; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")
        layout.addWidget(btn_finish)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def eventFilter(self, source, event):
        """Intercepte les événements clavier pour activer la soumission avec la touche 'Entrée'."""
        if source == self.command_input and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                # Simule le clic sur le bouton "Soumettre"
                self.submit_revision(self.questions[self.current_index])
                return True  # Indique que l'événement a été géré
        return super().eventFilter(source, event)

    def submit_revision(self, current_card):
        """Vérifie la réponse et met à jour la carte après révision."""
        user_command = self.command_input.toPlainText().strip()
        correct_answer = current_card['command'].strip()
        correct = user_command == correct_answer

        if 'box' not in current_card:
            current_card['box'] = 0  # Initialisation dans la boîte 1

        # Met à jour la boîte en fonction de la réussite ou de l'échec
        if correct:
            current_card['box'] = min(current_card['box'] + 1, 4)  # Passe à la boîte suivante (max boîte 5)
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

        for question, correct, correct_answer in self.results:
            # Affichage personnalisé pour les réponses correctes et incorrectes
            if correct:
                result_label = QLabel(f"✔ {question}: Correct!")
                result_label.setStyleSheet("font-size: 18px; color: green;")
            else:
                result_label = QLabel(f"✘ {question}: Incorrect! La bonne réponse est: {correct_answer}")
                result_label.setStyleSheet("font-size: 18px; color: red;")

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


# --------------------------------- Partie 3 Gestion des fiches --------------------------------------

    def init_view_cards(self):
        """Interface pour afficher toutes les cartes avec une UI améliorée et défilement vertical, avec options de modification."""
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

                # Affichage de la catégorie
                category_label = QLabel(f"Catégorie : {card.get('category', 'Aucune catégorie')}")
                category_label.setStyleSheet("font-size: 14px; color: #555;")
                card_layout.addWidget(category_label)

                # Ligne horizontale pour les boutons d'action
                action_layout = QHBoxLayout()

                # Bouton Supprimer avec icône
                btn_delete = QPushButton("Supprimer")
                btn_delete.setIcon(QIcon("icons/trash.png"))
                btn_delete.setStyleSheet("color: white; background-color: #e74c3c; border-radius: 4px; padding: 5px;")
                btn_delete.clicked.connect(partial(self.delete_card, card['question']))
                action_layout.addWidget(btn_delete)

                # Bouton Modifier Question
                btn_edit_question = QPushButton("Modifier Question")
                btn_edit_question.setIcon(QIcon("icons/edit.png"))
                btn_edit_question.setStyleSheet("color: white; background-color: #f39c12; border-radius: 4px; padding: 5px;")
                btn_edit_question.clicked.connect(partial(self.edit_card_field, card['question'], 'question'))
                action_layout.addWidget(btn_edit_question)

                # Bouton Modifier Réponse
                btn_edit_answer = QPushButton("Modifier Réponse")
                btn_edit_answer.setIcon(QIcon("icons/edit.png"))
                btn_edit_answer.setStyleSheet("color: white; background-color: #f39c12; border-radius: 4px; padding: 5px;")
                btn_edit_answer.clicked.connect(partial(self.edit_card_field, card['question'], 'answer'))
                action_layout.addWidget(btn_edit_answer)

                # Bouton Modifier Catégorie
                btn_edit_category = QPushButton("Modifier Catégorie")
                btn_edit_category.setIcon(QIcon("icons/edit.png"))
                btn_edit_category.setStyleSheet("color: white; background-color: #16a085; border-radius: 4px; padding: 5px;")
                btn_edit_category.clicked.connect(partial(self.edit_card_category, card['question']))
                action_layout.addWidget(btn_edit_category)

                # Bouton Déplacer avec menu déroulant pour sélectionner la boîte
                btn_move = QPushButton("Déplacer")
                btn_move.setIcon(QIcon("icons/move.png"))
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


    def edit_card_field(self, question, field):
        """Ouvre une boîte de dialogue pour modifier le champ spécifié (question ou réponse) d'une carte."""
        card = self.leitner_service.get_card_by_question(question)
        
        if not card:
            QMessageBox.warning(self, "Erreur", "Carte introuvable.")
            return

        # Boîte de dialogue pour l'édition
        dialog = QInputDialog(self)
        dialog.setWindowTitle(f"Modifier {field.capitalize()}")

        if field == 'question':
            dialog.setLabelText("Nouvelle question :")
            dialog.setTextValue(card['question'])
        elif field == 'answer':
            dialog.setLabelText("Nouvelle réponse :")
            dialog.setTextValue(card.get('answer', ""))  # Assurez-vous que la clé 'answer' existe

        if dialog.exec_() == QDialog.Accepted:
            new_value = dialog.textValue()
            
            if new_value:
                card[field] = new_value
                self.leitner_service.update_card(card)
                QMessageBox.information(self, "Modifié", f"La {field} a été mise à jour.")
            else:
                QMessageBox.warning(self, "Erreur", f"Le champ {field} ne peut pas être vide.")
        
        self.init_view_cards()

    def edit_card_category(self, question):
        """Permet de modifier la catégorie associée à une carte."""
        card = self.leitner_service.get_card_by_question(question)
        
        if not card:
            QMessageBox.warning(self, "Erreur", "Carte introuvable.")
            return

        # Boîte de dialogue pour l'édition de la catégorie
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Modifier Catégorie")
        dialog.setLabelText("Nouvelle catégorie :")
        dialog.setTextValue(card.get('category', ""))

        if dialog.exec_() == QDialog.Accepted:
            new_category = dialog.textValue()

            if new_category:
                card['category'] = new_category
                self.leitner_service.update_card(card)
                QMessageBox.information(self, "Modifié", f"La catégorie a été mise à jour.")
            else:
                QMessageBox.warning(self, "Erreur", "La catégorie ne peut pas être vide.")
        
        self.init_view_cards()


        
    def delete_card(self, question):
        """Supprime une carte."""
        self.leitner_service.delete_card(question)
        QMessageBox.information(self, "Supprimé", f"La carte '{question}' a été supprimée.")
        self.init_view_cards()



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

