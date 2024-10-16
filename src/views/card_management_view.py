import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
                            QWidget, QLineEdit, QTextEdit, QComboBox, QMessageBox, QFrame, 
                            QHBoxLayout, QScrollArea, QInputDialog, QDialog)
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, QEvent
from src.model import LeitnerService
from functools import partial
from datetime import datetime, timedelta

class CardManagementView(QWidget):
    def __init__(self):
        super().__init__()
        self.leitner_service = LeitnerService()  
        self.init_view_cards()

    def init_view_cards(self):
        """Interface pour afficher toutes les cartes avec une UI améliorée et défilement vertical, avec options de modification."""
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
                btn_edit_answer.clicked.connect(partial(self.edit_card_field, card['question'], 'command'))
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
        btn_back.clicked.connect(self.close)
        scroll_layout.addWidget(btn_back)

        # Mise en place du layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)  # Ajoutez la zone de défilement au layout principal
        self.setLayout(main_layout)


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
        elif field == 'command':
            dialog.setLabelText("Nouvelle réponse :")
            dialog.setTextValue(card.get('command', ""))

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
        card['next_revision'] = self.get_next_revision_time(target_box)
        self.leitner_service.update_card(card)

        QMessageBox.information(self, "Déplacé", f"La carte '{question}' a été déplacée vers la boîte {target_box + 1}.")
        self.init_view_cards()

