# Étape 3 : Récupération des métadonnées des articles

## 1. Objectif

Récupérer les **métadonnées complètes** de chaque article listé dans le fichier d'entrée. 

**Cette étape ne fait AUCUNE analyse de pertinence.** Tu récupères uniquement les données brutes.

**Fichier d'entrée :** `../data/articles.csv`  
**Fichiers de sortie :**
- `../results/articles_metadata.csv` — Données structurées de tous les articles
- `../results/articles_fetched.md` — Articles avec abstracts complets
- `../results/missing_abstracts.md` — Articles sans abstract (à compléter manuellement)

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

### 3.1 `articles_fetched.md`

Contient uniquement les articles avec **abstracts complets** :
- Titre, DOI, auteurs, journal, année, mots-clés
- Abstract complet en citation

### 3.2 `missing_abstracts.md`

Contient les articles dont l'abstract n'a **pas pu être récupéré** automatiquement.

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
- [ ] Le fichier `../results/articles_metadata.csv` existe et contient tous les articles
- [ ] Le fichier `../results/articles_fetched.md` existe avec les articles complets
- [ ] **Si `missing_abstracts.md` existe et contient des articles** → L'humain a été informé et a complété les abstracts
- [ ] Tous les articles ont un abstract (soit récupéré automatiquement, soit ajouté manuellement)

**Si tout est validé** → Passe à l'étape suivante : `./step4.md`

