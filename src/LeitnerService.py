import json
from datetime import datetime

class LeitnerService:
    def __init__(self):
        self.cards = []
        self.categories = []
        self.file_path = "leitner_cards.json"  # Fichier pour stocker les cartes
        self.category_file_path = "categories.json"
        self.load_cards()  # Charger les cartes lors de l'initialisation
        self.load_categories() 

    def add_card(self, card):
        # Ajouter une date de révision initiale lors de l'ajout de la carte
        card['last_revision'] = datetime.now().isoformat()  # On enregistre la date actuelle
        self.cards.append(card)
        self.save_cards()  # Sauvegarde après l'ajout

    def get_cards_by_box(self, box):
        """Récupère les cartes par boîte avec initialisation de 'last_revision' si nécessaire."""
        cards_in_box = [card for card in self.cards if card['box'] == box]
        
        # Initialiser 'last_revision' pour les cartes qui ne l'ont pas encore
        for card in cards_in_box:
            if 'last_revision' not in card:
                card['last_revision'] = datetime.now().isoformat()

        return cards_in_box

    def get_all_categories(self):
        """Retourne toutes les catégories."""
        return self.categories

    def add_category(self, category):
        """Ajoute une nouvelle catégorie si elle n'existe pas déjà."""
        if category not in self.categories:
            self.categories.append(category)
            self.save_categories()
    
    def save_categories(self):
        """Sauvegarde les catégories dans un fichier JSON."""
        with open(self.category_file_path, "w") as file:
            json.dump(self.categories, file)

    def load_categories(self):
        """Charge les catégories depuis un fichier JSON."""
        try:
            with open(self.category_file_path, "r") as file:
                self.categories = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.categories = [] 

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

    def get_card_by_question(self, question):
        """Récupère une carte spécifique par sa question."""
        for card in self.cards:
            if card['question'] == question:
                return card
        return None

    def get_cards_by_box_and_category(self, box, category):
        """
        Récupère les cartes qui sont dans la boîte spécifiée et correspondent à la catégorie donnée.
        """
        return [card for card in self.cards if card.get('box') == box and card.get('category') == category]
