import json

class LeitnerService:
    def __init__(self):
        self.cards = []
        self.file_path = "leitner_cards.json"  # Fichier pour stocker les cartes
        self.load_cards()  # Charger les cartes lors de l'initialisation

    def add_card(self, card):
        """Ajoute une carte au système."""
        self.cards.append(card)
        self.save_cards()  # Sauvegarde après l'ajout

    def get_cards_by_box(self, box):
        """Retourne toutes les cartes d'une boîte donnée."""
        return [card for card in self.cards if card['box'] == box]

    def update_card(self, updated_card):
        """Met à jour une carte dans la liste."""
        for card in self.cards:
            if card['question'] == updated_card['question']:
                card.update(updated_card)
        self.save_cards()  # Sauvegarde après la mise à jour

    def delete_card(self, question):
        """Supprime une carte."""
        self.cards = [card for card in self.cards if card['question'] != question]
        self.save_cards()  # Sauvegarde après la suppression

    def move_card(self, question, new_box):
        """Déplace une carte vers une nouvelle boîte."""
        for card in self.cards:
            if card['question'] == question:
                card['box'] = new_box
        self.save_cards()  # Sauvegarde après le déplacement

    def get_all_cards(self):
        """Retourne toutes les cartes."""
        return self.cards

    def save_cards(self):
        """Sauvegarde toutes les cartes dans un fichier JSON."""
        with open(self.file_path, "w") as file:
            json.dump(self.cards, file)

    def load_cards(self):
        """Charge les cartes depuis un fichier JSON."""
        try:
            with open(self.file_path, "r") as file:
                self.cards = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.cards = []  # Si le fichier n'existe pas ou est corrompu, on initialise avec une liste vide
