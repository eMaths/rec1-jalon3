# Étape 4 : Compréhension des articles

## 1. Objectif

Analyser et comprendre chaque article récupéré à l'étape 3 **sans effectuer de tri**.

Le même travail d'analyse fait pour la problématique (étape 2) doit être fait ici pour **chaque article** : identifier les thèmes, comprendre le message des auteurs, et produire une brève analyse.

**Fichiers d'entrée :**
- `../results/articles_fetched.md` — Métadonnées des articles avec abstracts
- `../results/articles_analysis.csv` — Fichier CSV à enrichir

**Fichiers de sortie :**
- `../results/articles_analysis.md` — Fiches d'analyse de chaque article
- `../results/articles_analysis.csv` — Mise à jour des colonnes `issue_type` et `justification`

---

## 2. Processus d'analyse

Pour **chaque article**, effectue les analyses suivantes :

### Étape 4.1 — Identification de la langue

Identifie si l'article est en **français** ou en **anglais**.

### Étape 4.2 — Analyse du titre

À partir du titre uniquement :

1. **Thèmes du titre** — Quels thèmes ressortent du titre ?
2. **Brève analyse** — En 1-2 phrases, que nous dit le titre sur le sujet de l'article ?

### Étape 4.3 — Analyse de l'abstract

À partir de l'abstract :

1. **Message des auteurs** — Qu'ont-ils voulu transmettre ? Qu'ont-ils fait ou montré ?
2. **Thèmes de l'abstract** — Quels thèmes ressortent de l'abstract ?
3. **Brève analyse** — En 2-3 phrases, de quoi parle l'article et quel est son apport ?

### Étape 4.4 — Détection d'état de l'art

Vérifie si l'article est **explicitement un état de l'art** (revue de littérature, survey, review, meta-analyse).

Indices à rechercher :

**Mots-clés indicateurs d'état de l'art :**
- review
- survey
- state of the art / état de l'art
- systematic review
- literature review
- scoping review
- meta-analysis
- overview
- mapping study

**Autres indices :**
- L'abstract mentionne explicitement l'analyse d'autres articles/études

| Résultat | Action |
|----------|--------|
| L'article est un état de l'art | → Marquer `Type : État de l'art` + mettre à jour le CSV |
| L'article n'est PAS un état de l'art | → Marquer `Type : Article original` + mettre à jour le CSV |

### Étape 4.5 — Mise à jour du CSV

Pour chaque article, mets à jour le fichier `../results/articles_analysis.csv` :

| Colonne | Valeur à remplir |
|---------|------------------|
| `issue_type` | "Article original" ou "État de l'art" |
| `justification` | Brève explication des thèmes identifiés (ex: "Thèmes: apprentissage automatique, détection de fraude") |

---

## 3. Règles d'analyse

### À faire
- Analyser **tous les articles** sans exception
- Identifier les thèmes du titre **séparément** des thèmes de l'abstract
- Être **factuel** et **concis** dans les analyses
- Expliquer clairement ce que les auteurs ont cherché à faire/montrer

### À ne pas faire
- **Trier** ou **rejeter** des articles — ce n'est PAS l'objectif de cette étape
- Juger de la pertinence par rapport à la problématique
- Inventer des informations non présentes dans le titre/abstract

---

## 4. Format du fichier de sortie

Le fichier `../results/articles_analysis.md` doit suivre ce format :

```markdown
# Analyse des articles

## Résumé

- **Total d'articles analysés :** [nombre]
- **Articles en français :** [nombre]
- **Articles en anglais :** [nombre]

---

## Fiches d'analyse

### Article 1 : [Titre de l'article]

- **Auteurs :** [liste des auteurs]
- **DOI :** [doi]
- **Langue :** français / anglais
- **Type :** Article original / État de l'art

#### Analyse du titre

**Thèmes identifiés :**
- [thème 1]
- [thème 2]
- [...]

**Brève analyse :**
[1-2 phrases expliquant ce que le titre nous dit sur le sujet]

#### Analyse de l'abstract

> [Abstract original]

**Message des auteurs :**
[Ce que les auteurs ont voulu transmettre, ce qu'ils ont fait ou montré]

**Thèmes identifiés :**
- [thème 1]
- [thème 2]
- [...]

**Brève analyse :**
[2-3 phrases sur le contenu et l'apport de l'article]

---

### Article 2 : [Titre]
[...]
```

---

## 5. Validation

Avant de passer à l'étape suivante, vérifie que :
- [ ] Le fichier `../results/articles_analysis.md` existe
- [ ] Le fichier `../results/articles_analysis.csv` a été mis à jour (colonnes `issue_type` et `justification`)
- [ ] **Tous** les articles ont été analysés (aucun exclu)
- [ ] Chaque fiche contient l'analyse du titre ET de l'abstract
- [ ] Les thèmes sont identifiés séparément pour le titre et l'abstract
- [ ] La langue de chaque article est identifiée
- [ ] Le type (article original ou état de l'art) est identifié pour chaque article

**Si tout est validé** → Passe à l'étape suivante : `./step5.md`
