import os
import google.generativeai as genai

# S'assurer que la config est ok
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def summarize(text, model_name):
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(text)
    return response.text

def split_chunks(text, size=4000):
    """Découpe le texte en morceaux (chunks) pour éviter les limites de tokens ou perdre le focus."""
    # Amélioration : split sur les doubles retours à la ligne pour ne pas couper de paragraphes en plein milieu
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        if len(current_chunk) + len(p) < size:
            current_chunk += p + "\n\n"
        else:
            chunks.append(current_chunk)
            current_chunk = p + "\n\n"
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def hierarchical_summary(text, config, lang="fr"):
    """Crée un résumé détaillé en fusionnant les résumés de différentes sections."""
    model_name = config["llm"]["model"]
    
    chunks = split_chunks(text)
    partials = []
    
    # 1. Résumé de chaque chunk (section)
    for i, chunk in enumerate(chunks):
        print(f"🧠 Analyse de la section {i+1}/{len(chunks)}...")
        prompt = f"Résume cette section technique avec précision (en {lang}):\n\n{chunk}"
        partials.append(summarize(prompt, model_name))
        
    # 2. Recomposition globale (le meta-résumé)
    print("🧠 Synthèse finale hiérarchique...")
    meta_prompt = (
        f"Voici un résumé des différentes parties d'un article technique.\n"
        f"Crée une synthèse logique, fluide et cohérente de toutes ces parties (en {lang}). "
        f"Conserve toute l'information clé et la valeur business/technique.\n\n" + 
        "\n---\n".join(partials)
    )
    
    return summarize(meta_prompt, model_name)
