import argparse
import hashlib
import json
import os
from pathlib import Path
import yaml

from audio_pipeline.ingestion import load_post
from audio_pipeline.summarizer import hierarchical_summary
from audio_pipeline.script_builder import build_short_script, build_long_script
from audio_pipeline.quarto_injector import inject_audio_metadata
from audio_pipeline.tts_engine import get_engine

import wave
from io import BytesIO

def get_audio_duration(file_path: Path):
    """Tente de récupérer la durée approximative d'un fichier audio sans dépendance lourde."""
    try:
        if file_path.suffix == '.wav':
            with wave.open(str(file_path), 'rb') as f:
                frames = f.getnframes()
                rate = f.getframerate()
                return int(frames / float(rate))
        # Pour le mp3, on fait une estimation très grossière basée sur le bitrate moyen 128kbps = 16kB/s
        # (L'idéal serait mutagen, mais on veut garder les deps légères)
        size_bytes = os.path.getsize(file_path)
        return int(size_bytes / 16000) 
    except Exception:
        return None

def get_md_hash(content: str, lang: str, model_name: str) -> str:
    """Calcule le hash du contenu et des paramètres pour le caching."""
    seed = f"{content}_{lang}_{model_name}"
    return hashlib.md5(seed.encode('utf-8')).hexdigest()

def main():
    parser = argparse.ArgumentParser("Générateur d'assets audio pour Quarto (Production Grade)")
    parser.add_argument("--post", required=True, help="Chemin vers le fichier index.qmd")
    parser.add_argument("--engine", default=None, help="Moteur (ex: gtts, qwen, coqui)")
    parser.add_argument("--format", choices=["short", "long", "both"], default="both", help="Format de l'audio à générer")
    parser.add_argument("--force", action="store_true", help="Ignorer le cache et tout regénérer (LLM et TTS)")
    parser.add_argument("--llm-only", action="store_true", help="S'arrêter après la génération LLM (utile pour debugger)")
    parser.add_argument("--tts-only", action="store_true", help="Ne lancer que le TTS (requiert que le cache LLM existe avec les bons scripts)")
    args = parser.parse_args()

    # Load Config
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    post_path = Path(args.post)
    print(f"\n🔄 Début de l'analyse : {post_path.parent.name}")
    
    # 1. Ingestion
    post = load_post(post_path)
    lang = post.get("lang", "en") # Détection automatique EN/FR
    slug = post['slug']
    print(f"🌍 Langue détectée : {lang.upper()}")
    
    # Stratégie de Caching : On compare le hash Markdown
    transcripts_dir = Path(config["paths"].get("transcripts_output", "assets/transcripts"))
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    cache_file = transcripts_dir / f"{slug}_cache.json"
    
    model_name = config["llm"]["model"]
    current_hash = get_md_hash(post["content"], lang, model_name)
    cache_data = {}
    
    if cache_file.exists() and not args.force:
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
        except Exception:
            pass # Fichier cache corrompu
            
    is_content_modified = cache_data.get("md_hash") != current_hash
    if is_content_modified and args.tts_only:
        print("⚠️ Attention: --tts-only demandé mais le contenu Markdown a changé (ou pas de cache).")
        print("➡️ Le LLM devra exceptionnellement être sollicité.")
        args.tts_only = False

    # 2. IA - Résumé & Scripts
    llm_updated = False
    if not args.tts_only and (is_content_modified or args.force or not cache_data.get("summary")):
        print("🧠 Génération/Mise à jour via LLM (Appel API encouru)...")
        summary = hierarchical_summary(post["content"], config, lang=lang)
        
        short_script = build_short_script(summary, lang=lang) if args.format in ["short", "both"] else None
        long_script = build_long_script(summary, lang=lang) if args.format in ["long", "both"] else None
        
        cache_data = {
            "md_hash": current_hash,
            "summary": summary,
            "short_script": short_script or cache_data.get("short_script"),
            "long_script": long_script or cache_data.get("long_script")
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print("💾 Cache LLM sauvegardé.")
        llm_updated = True
    else:
        print("⏭️ Cache LLM valide et préservé (Aucun appel API texte).")

    if args.llm_only:
        print("✅ Option --llm-only demandée. Arrêt du pipeline (TTS ignoré).")
        return

    # 3. Moteur TTS
    engine_name = args.engine or config["audio"]["default_engine"]
    print(f"\n🔧 Moteur TTS: {engine_name}")
    engine = get_engine(engine_name, config)

    # 4. Chemins Audio & Génération conditionnelle
    base_output = Path(config["paths"]["audio_output"])
    short_path_out = None
    long_path_out = None

    if args.format in ["short", "both"] and cache_data.get("short_script"):
        short_path = base_output / "short" / f"{slug}.mp3"
        short_path.parent.mkdir(parents=True, exist_ok=True)
        
        if short_path.exists() and not args.force and not llm_updated:
            print("⏭️ Audio Short déjà existant (skip).")
            short_path_out = short_path
        else:
            print("🎙️ Génération de l'audio Short (1~2min)...")
            engine.generate(cache_data["short_script"], short_path, lang=lang)
            short_path_out = short_path
            cache_data["duration_short"] = get_audio_duration(short_path)

    if args.format in ["long", "both"] and cache_data.get("long_script"):
        long_path = base_output / "long" / f"{slug}.mp3"
        long_path.parent.mkdir(parents=True, exist_ok=True)
        
        if long_path.exists() and not args.force and not llm_updated:
            print("⏭️ Audio Podcast déjà existant (skip).")
            long_path_out = long_path
        else:
            print("🎙️ Génération de l'audio Podcast (Deep Dive)...")
            try:
                engine.generate(cache_data["long_script"], long_path, lang=lang)
                long_path_out = long_path
                cache_data["duration_long"] = get_audio_duration(long_path)
            except Exception as e:
                print(f"⚠️ Échec du podcast sur ce moteur. Raison {e}")

    # MAJ du cache finale avec les durées si regénéré
    if args.format != "none":
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)

    # 5. Injection de la Metadata (seulement si généré ou skip existant)
    inject_audio_metadata(post_path, 
                          short_path_out, long_path_out, 
                          cache_data.get("duration_short"), cache_data.get("duration_long"))
    
    print("\n✅ Pipeline V2.1 complété avec succès !")

if __name__ == "__main__":
    main()
