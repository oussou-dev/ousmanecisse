import yaml
import xml.etree.ElementTree as ET
from email.utils import formatdate
from pathlib import Path
from audio_pipeline.ingestion import load_post
import os
import frontmatter

def duration_formatter(seconds):
    """Formatte des secondes en HH:MM:SS pour le podcast."""
    if not seconds:
        return "00:00:00"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def generate_podcast_rss(config):
    posts_dir = Path(config["paths"]["posts_dir"])
    fr_posts_dir = Path("fr") / config["paths"]["posts_dir"]
    base_url = "https://oussou-dev.github.io/ousmanecisse" # A dynamiser idéalement
    
    rss = ET.Element("rss", version="2.0", attrib={"xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"})
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = "Ousmane Cissé - AI Engineering Podcast"
    ET.SubElement(channel, "link").text = base_url
    ET.SubElement(channel, "description").text = "Deep Dives et résumés des articles techniques sur l'IA, les LLMs et les architectures Agents."
    ET.SubElement(channel, "language").text = "fr-FR"
    
    # On récupère tous les posts
    all_posts = list(posts_dir.rglob("index.qmd")) + list(fr_posts_dir.rglob("index.qmd"))
    
    for post_path in all_posts:
        try:
            post = load_post(post_path)
            # On relit le frontmatter original pour voir s'il y a un audio-podcast
            raw_post = frontmatter.load(post_path)
            
            # Ne publie que les Podcasts longs (Deep Dives) dans le flux RSS principal
            podcast_path = raw_post.get("audio-podcast")
            if not podcast_path:
                continue
                
            # Résolution propre du chemin web (du type ../../assets/audio/long/post.mp3)
            # Normalement le RSS est déposé à la racine du site, donc on re-calcule le chemin
            slug = post["slug"]
            audio_url = f"{base_url}/assets/audio/long/{slug}.mp3"
            
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = raw_post.get("title", slug)
            ET.SubElement(item, "description").text = raw_post.get("description", "Écoutez cet article technique.")
            ET.SubElement(item, "link").text = f"{base_url}/posts/{slug}/"
            
            # Enclosure obligatoire pour Apple/Spotify
            # TODO: Implémenter stat sur la taille du fichier lors de la génération pour être parfait
            ET.SubElement(item, "enclosure", url=audio_url, type="audio/mpeg", length="10485760") 
            ET.SubElement(item, "guid").text = audio_url
            
            # Date (approximation avec mtime si date non fournie)
            date = raw_post.get("date")
            pub_date = formatdate(os.path.getmtime(post_path)) if not date else date
            ET.SubElement(item, "pubDate").text = str(pub_date)
            
        except Exception as e:
            print(f"Erreur RSS sur {post_path}: {e}")

    # Sauvegarde du RSS à la racine du site
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ", level=0)
    output_rss = Path("_site") / "podcast.xml"
    output_rss.parent.mkdir(exist_ok=True)
    tree.write(output_rss, encoding="utf-8", xml_declaration=True)
    print(f"📻 Flux RSS du Podcast généré : {output_rss}")

if __name__ == "__main__":
    with open("config.yaml", "r") as f:
        generate_podcast_rss(yaml.safe_load(f))
