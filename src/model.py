import json
import os
from datetime import datetime

class LeitnerService:
    def __init__(self):
        self.cards = []
        self.categories = []
        self.file_path = "leitner_cards.json"  # Fichier pour stocker les cartes
        self.categories_file = "categories.json"  # Fichier pour stocker les catégories
        self.load_cards()  # Charger les cartes lors de l'initialisation
        self.load_categories()  # Charger les catégories lors de l'initialisation

    def load_categories(self):
        """Charge les catégories à partir du fichier JSON, et ajoute une catégorie spéciale 'All'."""
        if os.path.exists(self.categories_file):
            with open(self.categories_file, 'r') as f:
                self.categories = json.load(f)
        else:
            self.categories = []  # Si le fichier n'existe pas, initialise avec une liste vide

        if "All" not in self.categories:
            self.categories.insert(0, "All")  # Ajouter la catégorie spéciale "All" en première position

    def load_cards(self):
        """Charge les cartes depuis un fichier JSON."""
        try:
            with open(self.file_path, "r") as file:
                self.cards = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.cards = []  # Si le fichier n'existe pas ou est corrompu, on initialise avec une liste vide


    def add_category(self, category):
        if category not in self.categories:
            self.categories.append(category)

    def add_card(self, card):
        """Ajoute une nouvelle carte avec une date de révision initiale."""
        card['last_revision'] = datetime.now().isoformat()  # On enregistre la date actuelle
        self.cards.append(card)
        self.save_cards()  # Sauvegarde après l'ajout

    def get_all_categories(self):
        """Retourne une liste de toutes les catégories."""
        return list(set(card['category'] for card in self.cards if 'category' in card))
    
    def get_cards_by_box_and_category(self, box, category):
        """
        Récupère les cartes qui sont dans la boîte spécifiée et correspondent à la catégorie donnée.
        Si la catégorie est 'All', retourne toutes les cartes de la boîte spécifiée, sans filtrer par catégorie.
        """
        if category == "All":
            # Si la catégorie est "All", ne pas filtrer par catégorie
            return [card for card in self.cards if card.get('box') == box]
        else:
            # Filtrer à la fois par boîte et par catégorie
            return [card for card in self.cards if card.get('box') == box and card.get('category') == category]

    def update_card(self, updated_card):
        """Met à jour une carte dans la liste."""
        for card in self.cards:
            if card['question'] == updated_card['question']:
                card.update(updated_card)
        self.save_cards()  # Sauvegarde après la mise à jour

    def get_all_cards(self):
        """Retourne toutes les cartes."""
        return self.cards
    
    def get_card_by_question(self, question):
        """Récupère une carte spécifique par sa question."""
        for card in self.cards:
            if card['question'] == question:
                return card
        return None
    
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

    def save_cards(self):
        """Sauvegarde toutes les cartes dans un fichier JSON."""
        with open(self.file_path, "w") as file:
            json.dump(self.cards, file, indent=4)

