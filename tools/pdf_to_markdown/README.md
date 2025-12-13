# PDF to Markdown Converter for Scientific Articles

Script Python pour convertir des articles scientifiques PDF en Markdown avec préservation fidèle de la mise en forme.

## Fonctionnalités

- **Texte** : Extraction fidèle du contenu avec espacement correct
- **Sections** : Détection des titres (Abstract, Introduction, Methods, etc.)
- **Tableaux** : Conversion en tableaux Markdown
- **Listes** : Détection des listes à puces et numérotées
- **Formatage** : Gras, italique préservés
- **Références** : Section bibliographique conservée
- **Images** : Extraction optionnelle des figures

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### Ligne de commande

```bash
# Conversion simple (génère article.md)
python pdf_to_markdown.py article.pdf

# Spécifier le fichier de sortie
python pdf_to_markdown.py article.pdf -o output.md

# Extraire aussi les images
python pdf_to_markdown.py article.pdf --images
```

### En tant que module Python

```python
from pdf_to_markdown import pdf_to_markdown

# Convertir et sauvegarder
markdown = pdf_to_markdown("article.pdf", "output.md")

# Convertir avec extraction d'images
markdown = pdf_to_markdown("article.pdf", "output.md", extract_images=True)

# Convertir sans sauvegarder (retourne le texte)
markdown = pdf_to_markdown("article.pdf")
print(markdown)
```

## Dépendances

- **pymupdf4llm** : Bibliothèque optimisée pour la conversion PDF → Markdown

## Notes

- Optimisé pour les **articles scientifiques** (IEEE, ACM, Springer, etc.)
- Les PDF scannés (images) nécessitent un OCR préalable
- Les présentations PowerPoint converties en PDF peuvent donner des résultats moins bons
