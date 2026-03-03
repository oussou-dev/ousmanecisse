import os
import re
import argparse
import frontmatter
from pathlib import Path
import google.generativeai as genai
from gtts import gTTS
import requests
import base64
import json

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")
AUDIO_FILENAME = "audio-summary.mp3"

# Modèle pour le clonage de voix (utiliser Base pour le clonage)
HF_TTS_MODEL_CLONE = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
HF_TTS_MODEL_CUSTOM = "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"

def setup_gemini():
    if not GEMINI_API_KEY:
        print("❌ GOOGLE_API_KEY manquant.")
        return False
    genai.configure(api_key=GEMINI_API_KEY)
    return True

def clean_markdown(content):
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    content = re.sub(r'\{\{<.*?>\}\}', '', content)
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)
    content = re.sub(r'\n+', '\n', content).strip()
    return content

def generate_summary(text, lang="fr"):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = (
        f"Résume l'article suivant pour un audio de 1-2 min. Langue: {lang}. "
        f"Style: Podcast, engageant, chaleureux, professionnel. "
        f"Ne mentionne pas le code, focus sur la valeur ajoutée."
        f"\n\nContenu :\n{text}"
    )
    response = model.generate_content(prompt)
    return response.text

def tts_gtts(text, lang, output_path):
    print(f"🎙️ Utilisation de gTTS...")
    tts = gTTS(text=text, lang=lang)
    tts.save(output_path)

def tts_qwen_hf(text, lang, output_path, ref_audio=None, ref_text=None):
    """Appelle l'API Hugging Face avec option Voice Cloning"""
    if not HF_API_KEY:
        print("❌ HF_API_KEY manquante.")
        return tts_gtts(text, lang, output_path)

    model_id = HF_TTS_MODEL_CLONE if ref_audio else HF_TTS_MODEL_CUSTOM
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    payload = {
        "inputs": text,
        "parameters": {"src_lang": lang}
    }

    if ref_audio:
        print(f"👤 Activation du Voice Cloning (réf: {ref_audio})...")
        with open(ref_audio, "rb") as audio_file:
            audio_data = base64.b64encode(audio_file.read()).decode("utf-8")
        payload["parameters"]["ref_audio"] = audio_data
        if ref_text:
            payload["parameters"]["ref_text"] = ref_text

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Audio généré avec succès ({model_id}).")
        else:
            print(f"⚠️ Erreur HL API ({response.status_code}): {response.text}")
            tts_gtts(text, lang, output_path)
    except Exception as e:
        print(f"⚠️ Erreur: {e}. Repli sur gTTS.")
        tts_gtts(text, lang, output_path)

def update_qmd_with_player(qmd_path):
    with open(qmd_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    player_html = f'\n::: {{.callout-note appearance="simple"}}\n🎧 **Écouter le résumé audio**\n<audio controls src="{AUDIO_FILENAME}" style="width: 100%; border-radius: 8px;"></audio>\n:::\n'
    
    if AUDIO_FILENAME not in content:
        parts = content.split('---', 2)
        if len(parts) >= 3:
            parts[2] = player_html + parts[2]
            with open(qmd_path, 'w', encoding='utf-8') as f:
                f.write('---'.join(parts))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--post", help="Chemin vers index.qmd")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--engine", choices=["gtts", "qwen-hf"], default="gtts")
    parser.add_argument("--clone", help="Chemin vers ton fichier audio de référence (WAV/MP3 de 5-10s)")
    parser.add_argument("--clone-text", help="Texte exact dit dans l'audio de référence (améliore la qualité)")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not setup_gemini(): return

    posts = []
    if args.post: posts.append(Path(args.post))
    elif args.all: posts.extend(list(Path("posts").rglob("index.qmd")) + list(Path("fr/posts").rglob("index.qmd")))

    for p in posts:
        print(f"\n--- ⚡ Post : {p.parent.name} ---")
        post = frontmatter.load(p)
        lang = post.get('lang', 'en')
        output_audio = p.parent / AUDIO_FILENAME

        if output_audio.exists() and not args.force:
            print("⏭️ Déjà existant.")
            continue

        summary = generate_summary(clean_markdown(post.content), lang)
        
        if args.engine == "qwen-hf":
            tts_qwen_hf(summary, lang, output_audio, ref_audio=args.clone, ref_text=args.clone_text)
        else:
            tts_gtts(summary, lang, output_audio)

        update_qmd_with_player(p)

if __name__ == "__main__":
    main()
