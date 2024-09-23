from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QListWidget, QMessageBox
from LeitnerService import LeitnerService
from TerminalService import TerminalService

class LeitnerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.leitner_service = LeitnerService()
        self.terminal_service = TerminalService()

        self.setWindowTitle("Leitner App")
        self.setGeometry(300, 200, 600, 400)

        self.main_layout = QVBoxLayout()  # Crée un layout principal
        self.setLayout(self.main_layout)  # Définit le layout principal
        self.init_home()

    def init_home(self):
        self.clear_layout()  # Nettoyer le layout avant de charger l'interface
        layout = QVBoxLayout()

        self.question_choice = QPushButton("Enregistrer une nouvelle fiche", self)
        self.question_choice.clicked.connect(self.init_question_input)
        layout.addWidget(self.question_choice)

        self.revision_choice = QPushButton("Révisions", self)
        self.revision_choice.clicked.connect(self.init_revision)
        layout.addWidget(self.revision_choice)

        self.main_layout.addLayout(layout)  # Ajoute le nouveau layout au layout principal

    def init_question_input(self):
        self.clear_layout()  # Nettoyer l'interface actuelle
        layout = QVBoxLayout()

        self.question_input = QLineEdit(self)
        self.question_input.setPlaceholderText("Posez votre question ici...")
        layout.addWidget(QLabel("Question :"))
        layout.addWidget(self.question_input)

        self.command_input = QLineEdit(self)
        self.command_input.setPlaceholderText("Commande à exécuter...")
        layout.addWidget(QLabel("Commande :"))
        layout.addWidget(self.command_input)

        self.submit_button = QPushButton("Enregistrer", self)
        self.submit_button.clicked.connect(self.submit_question)
        layout.addWidget(self.submit_button)

        self.main_layout.addLayout(layout)  # Mettre à jour le layout principal

    def submit_question(self):
        question = self.question_input.text()
        command = self.command_input.text()

        if question and command:
            self.leitner_service.add_card(question, command)
            QMessageBox.information(self, "Succès", "Fiche enregistrée avec succès.")
            self.init_home()  # Retour à l'accueil
        else:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")

    def init_revision(self):
        self.clear_layout()  # Nettoyer l'interface actuelle
        layout = QVBoxLayout()
        
        self.question_list = QListWidget(self)
        self.question_list.addItems([card['question'] for card in self.leitner_service.cards])
        layout.addWidget(self.question_list)

        self.revision_button = QPushButton("Réviser", self)
        self.revision_button.clicked.connect(self.start_revision)
        layout.addWidget(self.revision_button)

        self.main_layout.addLayout(layout)  # Mettre à jour le layout principal

    def start_revision(self):
        if not self.question_list.currentItem():
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une question.")
            return
        
        selected_question = self.question_list.currentItem().text()
        command = self.leitner_service.get_command(selected_question)

        if command:
            self.clear_layout()  # Nettoyer l'interface actuelle
            layout = QVBoxLayout()

            self.terminal_output = QLineEdit(self)
            self.terminal_output.setPlaceholderText("Tapez la commande ici...")
            layout.addWidget(QLabel(f"Question : {selected_question}"))
            layout.addWidget(self.terminal_output)

            self.submit_revision_button = QPushButton("Soumettre", self)
            self.submit_revision_button.clicked.connect(lambda: self.check_answer(command))
            layout.addWidget(self.submit_revision_button)

            self.main_layout.addLayout(layout)  # Mettre à jour le layout principal
        else:
            QMessageBox.warning(self, "Erreur", "Aucune commande trouvée.")

    def check_answer(self, correct_command):
        user_command = self.terminal_output.text()
        if user_command == correct_command:
            QMessageBox.information(self, "Résultat", "Bonne réponse")
        else:
            QMessageBox.warning(self, "Résultat", "Mauvaise réponse")
        self.init_home()  # Retour à l'accueil

    def clear_layout(self):
        # Supprime tous les widgets et sous-layouts du layout principal
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_sub_layout(item.layout())

    def clear_sub_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_sub_layout(item.layout())
