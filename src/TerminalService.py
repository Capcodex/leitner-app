import subprocess

class TerminalService:
    def execute_command(self, command):
        try:
            # Exécution d'une commande de terminal
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout if result.stdout else result.stderr
        except Exception as e:
            return f"Erreur lors de l'exécution de la commande: {str(e)}"
