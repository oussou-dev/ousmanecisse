import frontmatter
from pathlib import Path

def load_post(path: Path):
    """Charge un post Quarto, extrait le frontmatter et nettoie le markdown."""
    post = frontmatter.load(path)
    
    # Simple nettoyage basique, on laisse le LLM faire le gros du travail de compréhension
    content = post.content
    
    return {
        "slug": path.parent.name,
        "content": content,
        "lang": post.get("lang", "en"),
        "title": post.get("title", ""),
        "description": post.get("description", "")
    }
