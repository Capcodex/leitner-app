from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
from LeitnerService import LeitnerService
from TerminalService import TerminalService

class ReviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout principal
        layout = QVBoxLayout()

        # Afficher la question
        self.question_label = QLabel("Question :")
        layout.addWidget(self.question_label)

        # Terminal pour entrer la réponse
        self.terminal_input = QTextEdit(self)
        layout.addWidget(QLabel("Répondez à la question dans le terminal :"))
        layout.addWidget(self.terminal_input)
        
        # Bouton pour vérifier la réponse
        self.submit_button = QPushButton("Soumettre")
        self.submit_button.clicked.connect(self.check_answer)
        layout.addWidget(self.submit_button)

        # Label pour afficher si la réponse est correcte ou non
        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        self.setLayout(layout)
        
        # Initialisation des services
        self.leitner_service = LeitnerService()
        self.terminal_service = TerminalService()

        self.current_card = self.leitner_service.get_next_card()

        if self.current_card:
            self.question_label.setText(f"Question : {self.current_card['question']}")
        else:
            self.question_label.setText("Pas de fiche disponible.")

    def check_answer(self):
        answer = self.terminal_input.toPlainText()
        correct_answer = self.current_card['answer']
        
        if answer.strip() == correct_answer.strip():
            self.result_label.setText("Bonne réponse")
        else:
            self.result_label.setText("Mauvaise réponse")
