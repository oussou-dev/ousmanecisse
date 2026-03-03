import os
import requests
from .base import TTSEngine

class QwenEngine(TTSEngine):
    def generate(self, text, output_path, lang="fr"):
        api_key = os.getenv("HF_API_KEY")
        if not api_key:
            print("❌ Clé HF_API_KEY manquante. Requis pour Qwen_HF.")
            return

        # Récupération conditionnelle du modèle Bilingue
        model_id = "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"
        try:
            voices = self.config.get("audio", {}).get("voices", {}).get("qwen", {})
            model_id = voices.get(lang, model_id)
        except Exception:
            pass

        url = f"https://api-inference.huggingface.co/models/{model_id}"
        headers = {"Authorization": f"Bearer {api_key}"}

        print(f"🎙️ [QwenHF - {lang.upper()}] API distante vers HuggingFace pour {output_path.name}...")
        
        # Limite API Inférence HuggingFace Gratuite (Approximatif)
        max_length = 800
        if len(text) > max_length:
            print("⚠️ Texte trop long, tronqué pour la démo HF API (Nécessitera l'interface Audio/Dataset ou Inference Endpoint Pro pour tout le podcast).")
            text = text[:max_length] + "..."

        payload = {
            "inputs": text,
            "parameters": {"src_lang": lang}
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=120)

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Génération HF Terminée.")
        else:
            print(f"❌ Erreur HF {response.status_code}: {response.text}")
