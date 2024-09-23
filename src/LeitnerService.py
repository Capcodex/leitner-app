class LeitnerService:
    def __init__(self):
        self.cards = []

    def add_card(self, question, command):
        card = {"question": question, "command": command, "level": 0}
        self.cards.append(card)

    def get_command(self, question):
        for card in self.cards:
            if card['question'] == question:
                return card['command']
        return None
