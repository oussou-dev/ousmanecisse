# 🎙️ Quarto Audio Pipeline (V2.1 - Production Grade)

Ce projet n'est plus un simple script, mais un véritable **Pipeline IA de Publication Multimodale**.
Il prend vos articles techniques rédigés en Markdown Quarto (`.qmd`) et les transforme en format audio (Résumé Rapide et Deep Dive Podcast) de manière intelligente, optimisée et robuste.

---

## 🏛️ Architecture & Fonctionnalités

*   **Ingestion IA Sûre** : Découpage (Chunking) du document et résumé hiérarchique via **Gemini 1.5 Flash**.
*   **Caching Intelligent (MD5)** : Le pipeline sauvegarde les transcripts et les audios générés. Gemini n'est appelé que si vous modifiez textuellement votre article, économisant ainsi drastiquement les appels API.
*   **Formats Découplés** : Choix entre générer un *Short* (90s), un *Podcast Long* (8m), ou les deux (`--format short|long|both`).
*   **Bilingue Natif** : Routage automatique vers des modèles TTS adaptés au français (`fr`) ou à l'anglais (`en`) selon le frontmatter de l'article Quarto.
*   **Injection Pandoc Lua** : L'injection dans le HTML est assurée au niveau compilation de l'AST Quarto par le filtre `audio_player.lua`. Aucune balise HTML polluante dans votre Markdown.
*   **Podcast RSS Ready** : Un script auxiliaire génère automatiquement un flux `podcast.xml` compatible Spotify/Apple.

---

## 🛠️ Installation

### 1. Dépendances

Installez les bibliothèques requises :

```bash
pip install python-frontmatter google-generativeai gTTS requests pyyaml
```

### 2. Configuration (`config.yaml`)

Toute l'architecture est paramétrable dans `scripts/config.yaml`.
Vous pouvez y configurer le modèle Gemini, sélectionner les voix par défaut ou définir les temps cibles.

### 3. Clés API (Variables d'environnement)

```bash
export GOOGLE_API_KEY="votre_cle_gemini"
export HF_API_KEY="votre_cle_hugging_face" # (Optionnel, requis pour Qwen-TTS)
```

---

## 🚀 Utilisation : Le CLI `cli.py`

Le point d'entrée unique du pipeline est désormais `scripts/cli.py`.

### Cas d'usage classiques

**1. Générer tous les formats (Short + Long) avec Qwen-TTS via HuggingFace :**
```bash
python scripts/cli.py --post posts/mon-article/index.qmd --engine qwen
```

**2. Générer uniquement le Podcast (Économie de temps/crédits) :**
```bash
python scripts/cli.py --post posts/mon-article/index.qmd --engine qwen --format long
```

**3. Tester uniquement la génération textuelle (Dry-run LLM) :**
*Idéal pour vérifier le script du podcast avant de consommer les API vocales.*
```bash
python scripts/cli.py --post posts/mon-article/index.qmd --llm-only
```

### ⚙️ Liste des paramètres CLI

| Paramètre | Description |
| :--- | :--- |
| `--post` | **(Requis)** Chemin vers un fichier `index.qmd` spécifique. |
| `--engine` | Moteur TTS (`gtts` par défaut, `qwen` recommandé). |
| `--format` | Format à générer (`short`, `long`, `both`). Défaut: `both`. |
| `--llm-only`| Lance uniquement Gemini et sauvegarde le script dans le cache JSON. Ignore le TTS. |
| `--tts-only`| Lance uniquement le moteur Vocal à partir du cache (si disponible et non expiré). |
| `--force` | Ignore le système de cache MD5 et force le recalcule par Gemini & le TTS. |

---

## 📻 Générer son flux Podcast RSS

Une fois que vous avez des articles disposant de la métadonnée `audio-podcast`, vous pouvez générer (ou mettre à jour) votre flux RSS global.

Depuis la racine du projet Quarto :

```bash
python scripts/audio_pipeline/podcast_feed.py
```

Cela créera un fichier `_site/podcast.xml` que vous pouvez soumettre aux plateformes de diffusion.

---

## ⚙️ Workflow Éditorial Recommandé

1. Rédigez votre article dans `/posts/mon-post/index.qmd`.
2. Lancez le pipeline (ex: `python scripts/cli.py --post posts/mon-post/index.qmd --engine qwen --format both`).
3. Vérifiez que votre `.qmd` contient désormais les métadonnées `audio-short`, `audio-podcast` et les `duration` associées.
4. Lancez `quarto render` pour recompiler le site Web (le filtre Lua fera apparaître les lecteurs audio au-dessus du texte).
5. Mettez le Flux RSS à jour.
6. `git commit` & Push vers le déploiement (Github Pages).
