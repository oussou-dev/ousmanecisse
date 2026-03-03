import os
import google.generativeai as genai

def generate_text_gemini(prompt, model_name="gemini-1.5-flash"):
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text

def build_short_script(summary: str, lang: str = "fr") -> str:
    """Génère le script court optimisé pour 60-90 sec."""
    prompt = f"""
    Tu es un ingénieur IA et créateur de contenu expérimenté.
    Transforme ce résumé en un script audio pour un "Short" très dynamique de 60 à 90 secondes.
    Langue : {lang}.
    Ton : Clair, posé, expert et engageant. Vas droit au but sur la valeur stratégique.
    Ne met pas d'indications scéniques (ex: [musique intro]). Uniquement le texte à vocaliser.
    \n\nContenu racine :\n{summary}
    """
    return generate_text_gemini(prompt)

def build_long_script(summary: str, lang: str = "fr") -> str:
    """Génère un script complet structuré (Podcast)."""
    prompt = f"""
    Crée un script vocal détaillé type "Deep Dive Podcast" (6-8 minutes) structuré en 6 parties claires :
    1. Hook (Accroche percutante)
    2. Contexte technique
    3. Problème résolu
    4. Analyse de la solution / Architecture
    5. Implications business & scalabilité
    6. Conclusion et ouverture
    
    Langue : {lang}.
    Ton : Expert qui discute avec ses pairs, didactique mais avancé.
    Ne met pas d'indications scéniques. Seulement le texte à prononcer de bout en bout.
    \n\nContenu racine :\n{summary}
    """
    return generate_text_gemini(prompt)
