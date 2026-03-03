from gtts import gTTS
from .base import TTSEngine
import time

class GTTSEngine(TTSEngine):
    def generate(self, text, output_path, lang="fr"):
        print(f"🎙️ [gTTS] Génération audio vers {output_path}...")
        tts = gTTS(text=text, lang=lang)
        tts.save(output_path)
        print("✅ Généré.")
