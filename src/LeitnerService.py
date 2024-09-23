# LeitnerService.py
import json
import os

class LeitnerService:
    def __init__(self):
        # Initialiser les boîtes avec des listes vides pour 5 boîtes (0 à 4)
        self.boxes = {i: [] for i in range(5)}
        self.load_data()  # Charger les données au démarrage

    def add_card(self, question, command):
        """Ajoute une fiche dans la boîte 1 (index 0)."""
        self.boxes[0].append({"question": question, "command": command})
        self.save_data()  # Sauvegarder après l'ajout

    def revise_card(self, question, correct):
        """Révise une fiche : la déplace ou la remet dans la boîte 1."""
        for box in range(5):
            for card in self.boxes[box]:
                if card['question'] == question:
                    if correct:
                        if box < 4:  # Ne pas dépasser la boîte 4
                            self.boxes[box].remove(card)
                            self.boxes[box + 1].append(card)  # Passer à la boîte suivante
                    else:
                        self.boxes[box].remove(card)
                        self.boxes[0].append(card)  # Renvoyer à la boîte 1
                    self.save_data()  # Sauvegarder après révision
                    return

    def get_cards_by_box(self, box_number):
        """Retourne les fiches de la boîte donnée."""
        return self.boxes[box_number]

    def save_data(self):
        """Sauvegarde les boîtes dans un fichier JSON."""
        try:
            with open('leitner_data.json', 'w') as f:
                json.dump(self.boxes, f)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données : {e}")

    def load_data(self):
        """Charge les données des boîtes à partir du fichier JSON."""
        if os.path.exists('leitner_data.json'):
            try:
                with open('leitner_data.json', 'r') as f:
                    self.boxes = json.load(f)
                    # Convertir les clés en entiers (elles peuvent être des chaînes après chargement JSON)
                    self.boxes = {int(k): v for k, v in self.boxes.items()}
            except Exception as e:
                print(f"Erreur lors du chargement des données : {e}")
                self.boxes = {i: [] for i in range(5)}  # Réinitialiser en cas d'échec
        else:
            # Si le fichier n'existe pas, on réinitialise les boîtes
            self.boxes = {i: [] for i in range(5)}
