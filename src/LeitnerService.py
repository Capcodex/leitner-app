class LeitnerService:
    def __init__(self):
        self.cards = []  # Liste des cartes

    def add_card(self, card):
        """Ajoute une carte au système."""
        self.cards.append(card)

    def get_cards_by_box(self, box):
        """Retourne toutes les cartes d'une boîte donnée."""
        return [card for card in self.cards if card['box'] == box]

    def update_card(self, updated_card):
        """Met à jour une carte dans la liste."""
        for card in self.cards:
            if card['question'] == updated_card['question']:
                card.update(updated_card)

    def delete_card(self, question):
        """Supprime une carte."""
        self.cards = [card for card in self.cards if card['question'] != question]

    def move_card(self, question, new_box):
        """Déplace une carte vers une nouvelle boîte."""
        for card in self.cards:
            if card['question'] == question:
                card['box'] = new_box

    def get_all_cards(self):
        """Retourne toutes les cartes."""
        return self.cards
