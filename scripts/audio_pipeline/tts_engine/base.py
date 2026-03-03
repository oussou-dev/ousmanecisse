class TTSEngine:
    def __init__(self, config):
        self.config = config

    def generate(self, text: str, output_path, lang="fr"):
        """Génère l'audio et sauvegarde le fichier au chemin output_path"""
        raise NotImplementedError("Les moteurs TTS héritants doivent implémenter `generate`")
