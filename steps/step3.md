# Étape 3 : Récupération des métadonnées des articles

## 1. Objectif

Récupérer les **métadonnées complètes** de chaque article listé dans le fichier d'entrée. 

**Cette étape ne fait AUCUNE analyse de pertinence.** Tu récupères uniquement les données brutes.

**Fichier d'entrée :** `../data/articles.csv`  
**Fichiers de sortie :**
- `../results/articles_analysis.csv` — **Fichier principal** qui sera enrichi à chaque étape
- `../results/articles_fetched.md` — Articles avec abstracts complets (français/anglais uniquement)
- `../results/missing_abstracts.md` — Articles sans abstract (à compléter manuellement)
- `../results/excluded_languages.md` — Articles exclus car dans une autre langue

---

## 2. Commandes disponibles

### Récupérer tous les articles

```bash
python3 ../tools/fetch_articles/fetch_all.py
```

### Récupérer un article spécifique (par DOI)

```bash
python3 ../tools/fetch_articles/fetch_article.py <DOI>
```

### Sources utilisées

Le script interroge automatiquement plusieurs APIs :

| Source | Description |
|--------|-------------|
| **OpenAlex** | Index académique ouvert (prioritaire) |
| **Semantic Scholar** | Base de données académique |
| **CrossRef** | Métadonnées DOI |
| **Europe PMC** | Articles biomédicaux |
| **Unpaywall** | Informations Open Access |

---

## 3. Fichiers de sortie

### 3.1 `articles_analysis.csv`

C'est le **fichier principal de suivi** qui sera enrichi tout au long du processus.

**Colonnes à créer à l'étape 3 :**

| Colonne | Description |
|---------|-------------|
| `title` | Titre de l'article |
| `abstract` | Abstract complet |
| `author` | Auteurs |
| `journal` | Nom du journal |
| `year` | Année de publication |
| `doi` | DOI de l'article |
| `keywords` | Mots-clés |
| `language` | Langue (fr/en) |
| `issue_type` | À remplir étape 4 : "Article original" ou "État de l'art" |
| `selection` | À remplir étape 5 : "Retenu" ou "Rejeté" |
| `justification` | À remplir étapes 4-5 : explication brève |

### 3.2 `articles_fetched.md`

Contient uniquement les articles avec **abstracts complets** :
- Titre, DOI, auteurs, journal, année, mots-clés
- Abstract complet en citation

### 3.3 `missing_abstracts.md`

Contient les articles dont l'abstract n'a **pas pu être récupéré** automatiquement.

### 3.4 `excluded_languages.md`

Contient les articles **exclus automatiquement** car ils ne sont ni en français ni en anglais.

> ⚠️ **Attention aux hallucinations** : La langue doit être déterminée à partir des **métadonnées retournées par les APIs** (champ `language` ou similaire), PAS en devinant à partir du titre. Si la langue n'est pas explicitement indiquée dans les métadonnées, considérer l'article comme valide (ne pas l'exclure).

**Format :**

```markdown
# Articles sans abstract

Ces articles nécessitent une intervention manuelle.

## Instructions pour l'humain

1. Pour chaque article ci-dessous, récupérez l'abstract manuellement
2. Ajoutez l'abstract dans ce fichier à l'emplacement indiqué
3. Une fois tous les abstracts complétés, relancez l'étape 4

---

### Article 1 : [Titre]

- **DOI :** [doi]
- **Lien :** [https://doi.org/doi]

**Abstract (à compléter) :**

> [COLLER L'ABSTRACT ICI]

---
```

---

## 4. Gestion des abstracts manquants

### Si `missing_abstracts.md` contient des articles :

⚠️ **STOP** — Ne passe PAS à l'étape 4 immédiatement.

1. **Informe l'humain** qu'il y a des abstracts manquants
2. **Attends** que l'humain complète le fichier `missing_abstracts.md`
3. Une fois complété, **fusionne** les abstracts dans `articles_fetched.md`
4. Puis passe à l'étape 4

### Message à afficher à l'humain :

```
⚠️ ATTENTION : [N] article(s) n'ont pas d'abstract récupérable automatiquement.

Veuillez compléter le fichier : results/missing_abstracts.md

Pour chaque article listé :
1. Ouvrez le lien DOI dans votre navigateur
2. Copiez l'abstract depuis la page de l'article
3. Collez-le dans le fichier à l'emplacement indiqué

Une fois terminé, dites-moi "c'est fait" pour continuer.
```

---

## 5. Validation

Avant de passer à l'étape suivante, vérifie que :
- [ ] Le fichier `../results/articles_analysis.csv` existe avec les colonnes de base remplies
- [ ] Le fichier `../results/articles_fetched.md` existe avec les articles complets
- [ ] **Si `missing_abstracts.md` existe et contient des articles** → L'humain a été informé et a complété les abstracts
- [ ] **Si `excluded_languages.md` existe** → L'humain a été notifié des articles exclus
- [ ] Tous les articles retenus sont en français ou en anglais
- [ ] Tous les articles retenus ont un abstract

**Si tout est validé** → Passe à l'étape suivante : `./step4.md`

