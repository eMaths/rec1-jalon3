# Étape 6 : Téléchargement des articles

## 1. Objectif

Télécharger les **PDFs complets** des articles retenus à l'étape 5 pour permettre une analyse approfondie.

**Fichiers d'entrée :**
- `../results/final_selection.md` — Articles validés (étape 5)

**Fichiers de sortie :**
- `../results/pdfs/` — Dossier contenant les PDFs téléchargés
- `../results/download_report.md` — Rapport de téléchargement
- `../results/unavailable_articles.md` — Articles non accessibles (si applicable)

---

## 2. Commandes disponibles

### Télécharger tous les articles sélectionnés

```bash
python3 ../tools/download_pdfs/download_all.py
```

### Vérifier l'accessibilité d'un article spécifique

```bash
python3 ../tools/download_pdfs/download_pdf.py --check <DOI>
```

### Télécharger un article spécifique

```bash
python3 ../tools/download_pdfs/download_pdf.py <DOI>
python3 ../tools/download_pdfs/download_pdf.py <DOI> --output ../results/pdfs/
```

---

## 3. Sources de téléchargement

Le script télécharge automatiquement les PDFs depuis des sources Open Access :

| Source | Type | Description |
|--------|------|-------------|
| **Unpaywall** | API | Base de données d'accès ouvert légal |
| **OpenAlex** | API | Index académique ouvert |
| **Semantic Scholar** | API | PDFs Open Access |
| **arXiv** | Direct | Preprints (si lien arXiv) |
| **Europe PMC** | API | Articles biomédicaux |

---

## 4. Gestion des articles non accessibles

### Si `unavailable_articles.md` contient des articles :

⚠️ **STOP** — Certains articles ne sont pas en Open Access.

1. **Informe l'humain** qu'il y a des articles non accessibles
2. **Attends** que l'humain récupère les PDFs manuellement
3. Une fois les PDFs ajoutés dans `results/pdfs/`, continue

### Message à afficher à l'humain :

```
⚠️ ATTENTION : [N] article(s) ne sont pas accessibles en Open Access.

Veuillez récupérer manuellement les PDFs listés dans : results/unavailable_articles.md

Options pour récupérer les articles :
1. Accès via votre bibliothèque universitaire
2. Demande aux auteurs (ResearchGate, email)
3. Achat sur le site de l'éditeur

Placez les PDFs dans : results/pdfs/
Nommez-les selon le format indiqué dans le fichier.

Une fois terminé, dites-moi "c'est fait" pour continuer.
```

---

## 5. Validation

Avant de passer à l'étape suivante, vérifie que :
- [ ] Le dossier `../results/pdfs/` existe et contient des PDFs
- [ ] Le fichier `../results/download_report.md` existe
- [ ] **Si `unavailable_articles.md` existe** → L'humain a été informé et a ajouté les PDFs manquants
- [ ] Tous les articles retenus ont un PDF disponible

**Si tout est validé** → Passe à l'étape suivante : `./step7.md`
