from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel
from LeitnerService import LeitnerService
from TerminalService import TerminalService

class AddCardWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principal
        layout = QVBoxLayout()

        # Entrer la question
        self.question_input = QLineEdit(self)
        self.question_input.setPlaceholderText("Posez votre question ici...")
        layout.addWidget(QLabel("Question :"))
        layout.addWidget(self.question_input)
        
        # Terminal pour entrer la commande correcte
        self.terminal_output = QTextEdit(self)
        layout.addWidget(QLabel("Terminal :"))
        layout.addWidget(self.terminal_output)
        
        # Bouton pour enregistrer la fiche
        self.submit_button = QPushButton("Enregistrer")
        self.submit_button.clicked.connect(self.save_card)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        
        # Initialisation des services
        self.leitner_service = LeitnerService()
        self.terminal_service = TerminalService()

    def save_card(self):
        question = self.question_input.text()
        command = self.terminal_output.toPlainText()
        
        if question and command:
            self.leitner_service.add_card(question, command)
            self.question_input.clear()
            self.terminal_output.clear()
            print(f"Question enregistrée: {question}")
