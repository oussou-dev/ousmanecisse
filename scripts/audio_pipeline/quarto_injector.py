"""Module central pour injecter les variables audio dans les metadata du post."""
import os
import frontmatter
from pathlib import Path

def get_relative_url(qmd_path: Path, audio_file: Path):
    """Calcule le chemin de l'audio relatif au post Quarto pour l'URL web."""
    # os.path.relpath("assets/audio/short/foo.mp3", "posts/foo")
    # -> "../../assets/audio/short/foo.mp3"
    return os.path.relpath(audio_file, start=qmd_path.parent)

def inject_audio_metadata(qmd_path: Path, short_audio: Path = None, long_audio: Path = None, duration_short=None, duration_long=None):
    """
    On injecte proprement dans le yaml Frontmatter au lieu de hardcoder du HTML.
    Cela permet ensuite au système Quarto d'afficher les lecteurs de manière native
    avec un include-before-body par exemple.
    On ne supprime pas les anciennes clés si elles existent et qu'on ne les met pas à jour.
    """
    with open(qmd_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)
        
    if short_audio:
        post["audio-short"] = get_relative_url(qmd_path, short_audio)
        if duration_short: post["duration-short"] = duration_short
    if long_audio:
        post["audio-podcast"] = get_relative_url(qmd_path, long_audio)
        if duration_long: post["duration-podcast"] = duration_long
    
    with open(qmd_path, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))
        
    print(f"✅ Metadata Quarto injectées dans {qmd_path.name}")
