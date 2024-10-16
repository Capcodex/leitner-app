from PySide6.QtWidgets import (QPushButton, QLabel, QVBoxLayout, QWidget, 
                               QComboBox, QMessageBox, QFrame, QHBoxLayout, 
                               QScrollArea, QInputDialog, QDialog, QLineEdit)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from src.model import LeitnerService
from functools import partial

class CardManagementView(QWidget):
    def __init__(self):
        super().__init__()
        self.leitner_service = LeitnerService()
        self.scroll_layout = None  # Définir l'attribut ici
        self.init_view_cards()

    def init_view_cards(self):
        """Interface pour afficher toutes les cartes avec une UI améliorée et défilement vertical."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)  # Définir self.scroll_layout ici

        # Champ de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par mot-clé...")
        self.search_input.textChanged.connect(self.update_card_view)  # Mettre à jour les cartes lors de la recherche
        self.scroll_layout.addWidget(self.search_input)

        # Filtre par catégorie
        self.category_combo = QComboBox()
        self.category_combo.addItem("Toutes les catégories")

        # Ajouter dynamiquement les catégories à partir du modèle
        categories = self.leitner_service.get_all_categories()
        for category in categories:
            self.category_combo.addItem(category)

        self.category_combo.currentIndexChanged.connect(self.update_card_view)
        self.scroll_layout.addWidget(self.category_combo)

        # Ajoutez un espace de séparation (optionnel) pour l'esthétique
        self.scroll_layout.addSpacing(10)

        # Initialiser l'affichage des cartes
        self.display_cards()  # Afficher les cartes lors de l'initialisation

        scroll_area.setWidget(scroll_content)
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def display_cards(self):
        """Affiche toutes les cartes dans le layout après application des filtres."""
        # Effacez les anciens widgets
        for i in reversed(range(self.scroll_layout.count())): 
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None and widget not in [self.search_input, self.category_combo]:
                widget.deleteLater()

        all_cards = self.leitner_service.get_all_cards()
        filtered_cards = self.filter_cards(all_cards)

        if not filtered_cards:
            empty_label = QLabel("Aucune carte n'a été trouvée.")
            empty_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(empty_label)
        else:
            for card in filtered_cards:
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
                self.scroll_layout.addWidget(card_frame)

    def filter_cards(self, cards):
        """Filtre les cartes selon le mot-clé et la catégorie."""
        keyword = self.search_input.text().lower()
        category = self.category_combo.currentText()

        filtered_cards = []
        for card in cards:
            if (keyword in card['question'].lower() or keyword in card.get('command', '').lower()) and \
               (category == "Toutes les catégories" or card.get('category', '') == category):
                filtered_cards.append(card)

        return filtered_cards

    def update_card_view(self):
        """Met à jour l'affichage des cartes selon les filtres appliqués."""
        self.display_cards()  # Appeler display_cards pour afficher les cartes

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

            self.update_card_view()

    def edit_card_category(self, question):
        """Permet de modifier la catégorie associée à une carte."""
        card = self.leitner_service.get_card_by_question(question)

        if not card:
            QMessageBox.warning(self, "Erreur", "Carte introuvable.")
            return

        new_category, ok = QInputDialog.getItem(self, "Modifier Catégorie", 
                                                 "Sélectionnez une nouvelle catégorie :",
                                                 self.leitner_service.get_all_categories(), editable=True)

        if ok and new_category:
            card['category'] = new_category
            self.leitner_service.update_card(card)
            self.update_card_view()

    def delete_card(self, question):
        """Supprime une carte en fonction de la question."""
        card = self.leitner_service.get_card_by_question(question)
        if not card:
            QMessageBox.warning(self, "Erreur", "Carte introuvable.")
            return

        confirm = QMessageBox.question(self, "Confirmer", f"Êtes-vous sûr de vouloir supprimer la carte : '{question}' ?",
                                        QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.Yes:
            self.leitner_service.delete_card(card['question'])
            self.update_card_view()

    def move_card(self, question, combo_box):
        """Déplace une carte vers une nouvelle boîte."""
        card = self.leitner_service.get_card_by_question(question)

        if not card:
            QMessageBox.warning(self, "Erreur", "Carte introuvable.")
            return

        box_index = combo_box.currentIndex()  # Récupérer l'index de la boîte sélectionnée
        card['box'] = box_index
        self.leitner_service.update_card(card)
        self.update_card_view()
