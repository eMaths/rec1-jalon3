# Étape 3 : Récupération des métadonnées des articles

## 1. Objectif

Récupérer les **métadonnées complètes** de chaque article listé dans le fichier d'entrée. 

**Cette étape ne fait AUCUNE analyse de pertinence.** Tu récupères uniquement les données brutes.

**Fichier d'entrée :** `../data/articles.csv`  
**Fichiers de sortie :**
- `../results/articles_metadata.csv` — Données structurées de tous les articles
- `../results/articles_fetched.md` — Log détaillé du processus de récupération

---

## 2. Outil disponible

### `fetch_article.py` — Récupération des métadonnées d'un article

**Localisation :** `../tools/fetch_articles/fetch_article.py`

**Fonction :** Récupère les métadonnées d'un article via son DOI en interrogeant plusieurs APIs (OpenAlex, Semantic Scholar, CrossRef, Unpaywall).

**Usage (un seul article) :**
```bash
python ../tools/fetch_articles/fetch_article.py <DOI>
```

**Usage (tous les articles d'un coup) :**
```bash
python ../tools/fetch_articles/fetch_article.py --batch ../data/articles.csv --output ../results/articles_metadata.csv
```

**Sortie JSON (par article) :**
| Champ | Description |
|-------|-------------|
| `doi` | Identifiant DOI de l'article |
| `title` | Titre de l'article |
| `authors` | Liste des auteurs |
| `abstract` | Résumé de l'article |
| `journal` | Nom du journal/conférence |
| `year` | Année de publication |
| `keywords` | Mots-clés associés |
| `success` | `true` si la récupération a réussi |
| `source` | API source des données |

---

## 3. Processus à suivre

### Étape 3.1 — Exécution du script
1. Exécute le script en mode batch pour traiter tous les articles en une seule commande
2. Si le mode batch n'est pas disponible, traite les articles un par un

### Étape 3.2 — Collecte des résultats
Pour chaque article, collecte :
- Les métadonnées récupérées (titre, auteurs, abstract, etc.)
- Le statut de la récupération (succès/échec)
- Le message d'erreur en cas d'échec

### Étape 3.3 — Génération des fichiers de sortie
Produis les deux fichiers de sortie décrits ci-dessous.

---

## 4. Format des fichiers de sortie

### 4.1 Fichier CSV : `../results/articles_metadata.csv`

Colonnes requises :

```csv
doi,title,authors,abstract,journal,year,keywords,fetch_status
```

| Colonne | Description |
|---------|-------------|
| `doi` | DOI de l'article |
| `title` | Titre récupéré |
| `authors` | Auteurs (séparés par `;`) |
| `abstract` | Résumé complet |
| `journal` | Nom du journal |
| `year` | Année de publication |
| `keywords` | Mots-clés (séparés par `;`) |
| `fetch_status` | `success` ou `error: [message]` |

### 4.2 Fichier Markdown : `../results/articles_fetched.md`

Ce fichier sert de **log de traçabilité**. Il doit suivre ce squelette :

```markdown
# Log de récupération des métadonnées

## Résumé

- **Total d'articles traités :** [nombre]
- **Récupérations réussies :** [nombre]
- **Échecs :** [nombre]

---

## Articles récupérés avec succès

### Article 1 : [Titre de l'article]

- **DOI :** [doi]
- **Auteurs :** [liste des auteurs]
- **Journal :** [nom du journal]
- **Année :** [année]
- **Mots-clés :** [liste des mots-clés]
- **Abstract :**

> [Résumé de l'article]

---

### Article 2 : [Titre]
[...]

---

## Échecs de récupération

| DOI | Erreur |
|-----|--------|
| [doi] | [message d'erreur] |
| [...] | [...] |
```

---

## 5. Règles à respecter

### À faire
- Traiter **tous** les articles du fichier d'entrée
- Conserver les données **même partielles** (si seul le titre est disponible, le noter)
- Documenter **chaque échec** avec le message d'erreur

### À ne pas faire
- **Analyser la pertinence des articles** (ce sera fait à l'étape 4)
- Ignorer silencieusement les erreurs
- Modifier le fichier d'entrée `../data/articles.csv`
- Inventer des données manquantes

---

## 6. Validation

Avant de passer à l'étape suivante, vérifie que :
- [ ] Le fichier `../results/articles_metadata.csv` existe et contient tous les articles
- [ ] Le fichier `../results/articles_fetched.md` existe avec le résumé et le détail
- [ ] Chaque article a un statut (succès ou erreur documentée)
- [ ] Les données essentielles (titre, abstract, auteurs) sont présentes pour les succès

**Si tout est validé** → Passe à l'étape suivante : `./step4.md`

