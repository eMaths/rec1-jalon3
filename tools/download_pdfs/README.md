# Download PDFs - Téléchargement d'articles scientifiques

Outils pour télécharger les PDFs d'articles scientifiques depuis des sources Open Access.

## Sources utilisées

| Source | Type | Description |
|--------|------|-------------|
| **Unpaywall** | API | Base de données d'accès ouvert légal |
| **OpenAlex** | API | Index académique ouvert |
| **Semantic Scholar** | API | PDFs Open Access |
| **arXiv** | Direct | Preprints (si lien arXiv) |
| **Europe PMC** | API | Articles biomédicaux |

## Usage

### Télécharger un seul article

```bash
python download_pdf.py 10.1234/example.doi
```

### Vérifier l'accessibilité sans télécharger

```bash
python download_pdf.py --check 10.1234/example.doi
```

### Télécharger depuis une liste de DOIs

```bash
python download_pdf.py --file dois.txt --output ./pdfs/
```

### Télécharger tous les articles sélectionnés

```bash
python download_all.py
```

Ce script lit `results/final_selection.md` (ou `candidates.md`) et télécharge tous les PDFs dans `results/pdfs/`.

## Fichiers générés

| Fichier | Description |
|---------|-------------|
| `results/pdfs/` | Dossier contenant les PDFs téléchargés |
| `results/download_report.md` | Rapport de téléchargement |
| `results/unavailable_articles.md` | Articles non accessibles (à récupérer manuellement) |

## Limitations

- Seuls les articles en **Open Access** peuvent être téléchargés automatiquement
- Les articles payants nécessitent un accès institutionnel ou un achat
- Respecte les rate limits des APIs (0.5s entre chaque requête)

## Dépendances

Aucune dépendance externe requise (utilise uniquement la bibliothèque standard Python).
