from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QComboBox, QWidget, QMessageBox # type: ignore
from PySide6.QtCore import Qt, QEvent # type: ignore
from src.model import LeitnerService

class AddCardView(QWidget):
    def __init__(self):
        super().__init__()
        self.leitner_service = LeitnerService()  # Vous pourriez vouloir passer le service comme argument
        self.init_add_card_view()

    def init_add_card_view(self):
        """Interface pour ajouter une nouvelle fiche."""
        layout = QVBoxLayout()
        self.setGeometry(100, 100, 800, 600)

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
        self.category_input.addItem("All")  # Ajouter "All" comme option par défaut
        self.category_input.addItem("Sélectionnez ou ajoutez une catégorie")
        self.category_input.addItems(self.leitner_service.categories)  # Charger les catégories existantes
        self.category_input.setEditable(True)  # Permettre à l'utilisateur d'ajouter une nouvelle catégorie
        self.category_input.setStyleSheet("font-size: 16px; padding: 8px;")

        # Définir "All" comme la catégorie sélectionnée par défaut
        self.category_input.setCurrentIndex(0)

        # Bouton d'enregistrement
        btn_submit = QPushButton("Enregistrer")
        btn_submit.clicked.connect(self.submit_question)
        btn_submit.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")

        # Bouton de retour
        btn_back = QPushButton("Retour")
        btn_back.clicked.connect(self.close)
        btn_back.setStyleSheet("background-color: #d9534f; color: white; padding: 10px; font-size: 16px; border-radius: 5px;")

        # Ajout des widgets au layout
        layout.addWidget(self.question_input)
        layout.addWidget(self.command_input)
        layout.addWidget(self.category_input)
        layout.addWidget(btn_submit)
        layout.addWidget(btn_back)

        self.setLayout(layout)

    def eventFilter(self, source, event):
            """Intercepte les événements clavier pour activer la soumission avec Ctrl + Entrée."""
            if source == self.command_input and event.type() == QEvent.KeyPress:
                if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and event.modifiers() == Qt.ControlModifier:
                    # Simule le clic sur le bouton "Soumettre" ou "Question suivante"
                    if self.btn_submit.text() == "Enregistrer":
                        self.submit_question()
                    else:
                        pass
                    return True  # Indique que l'événement a été géré
            return super().eventFilter(source, event)

    def submit_question(self):
        """Soumettre une nouvelle fiche et l'enregistrer dans la boîte 1."""
        question = self.question_input.text()
        command = self.command_input.toPlainText()
        category = self.category_input.currentText()

        if question and command:
            if category and category not in self.leitner_service.get_all_categories():
                self.leitner_service.add_category(category)

            card = {
                'question': question,
                'command': command,
                'box': 0,
                'category': category
            }
            self.leitner_service.add_card(card)
            QMessageBox.information(self, "Enregistré", f"La carte '{question}' a été ajoutée.")
            self.close()
