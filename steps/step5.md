# Étape 5 : Tri et sélection des articles

## 1. Objectif

Trier les articles analysés à l'étape 4 pour déterminer leur **pertinence par rapport à la problématique**.

Cette sélection est faite **par toi** (l'IA), en te basant sur :
- Les **fiches de compréhension** de l'étape 4
- Les **thèmes identifiés** à l'étape 2 (`../results/themes.json`)

**Fichiers d'entrée :**
- `../results/articles_analysis.md` — Fiches de compréhension des articles (étape 4)
- `../results/articles_analysis.csv` — Fichier CSV à enrichir
- `../results/themes.json` — Thèmes de référence (primaires, secondaires, voisins)

**Fichiers de sortie :**
- `../results/selection_report.md` — Rapport de sélection des articles
- `../results/articles_analysis.csv` — **Fichier final** avec colonnes `selection` et `justification` complétées

---

## 2. Processus d'analyse

Pour **chaque article**, applique le processus suivant dans l'ordre :

### Étape 5.1 — Comparaison avec les thèmes

Pour chaque article, compare les **thèmes identifiés dans sa fiche** (step 4) avec les thèmes du fichier `../results/themes.json`.

| Résultat | Action |
|----------|--------|
| Les thèmes de l'article correspondent à un ou plusieurs thèmes du JSON | → Retenir l'article |
| Aucun thème de l'article ne correspond aux thèmes du JSON | → Rejeter l'article |

### Étape 5.2 — Classification par catégorie

Pour les articles retenus, indique à quelle catégorie de thèmes ils correspondent :
- **A. Thème primaire** — Lien direct avec la problématique
- **B. Thème secondaire** — Lien indirect, peut contribuer à la réponse
- **C. Thème voisin** — Même domaine, mais ne répond pas à la problématique

### Étape 5.3 — Mise à jour du CSV

Pour chaque article, mets à jour le fichier `../results/articles_analysis.csv` :

| Colonne | Valeur à remplir |
|---------|------------------|
| `selection` | "Retenu" ou "Rejeté" |
| `justification` | Compléter avec la raison de la décision |

**Format de la justification (brève mais explicite) :**

| Cas | Exemple de justification |
|-----|-------------------------|
| Retenu par le titre | "Titre: traite de [thème X] en lien direct avec la problématique" |
| Retenu par l'abstract | "Abstract: méthode de [X] applicable à [Y]" |
| État de l'art retenu | "État de l'art sur [thème X], synthèse utile" |
| Rejeté | "Hors sujet: traite de [thème Z] sans lien avec la problématique" |

---

## 3. Règles d'analyse

### À faire
- Te baser sur les **fiches de compréhension** de l'étape 4 (pas sur tes connaissances externes)
- Justifier **chaque décision** avec des arguments concrets
- Lister les thèmes abordés dans l'article par ordre de prédominance
- Être **cohérent** avec les thèmes définis dans `../results/themes.json`

### À ne pas faire
- Accepter un article sans justification
- Rejeter un article sans explication claire
- Inventer des informations non présentes dans le titre/abstract
- Modifier les fichiers d'entrée

---

## 4. Format du fichier de sortie

Le fichier `../results/selection_report.md` doit suivre **exactement** ce squelette :

```markdown
# Analyse de pertinence des articles

## Résumé

- **Total d'articles analysés :** [nombre]
- **Articles retenus (pertinents) :** [nombre]
- **Articles rejetés (non pertinents) :** [nombre]

### Répartition des articles retenus par catégorie

| Catégorie | Nombre |
|-----------|--------|
| A. Thèmes primaires | [nombre] |
| B. Thèmes secondaires | [nombre] |
| C. Thèmes voisins | [nombre] |

---

## Articles analysés

### Article 1 : [Titre de l'article]

- **Auteurs :** [liste des auteurs]
- **DOI :** [doi]
- **Lien :** [https://doi.org/doi]

#### Abstract

> [Résumé de l'article]

#### Thèmes identifiés (par ordre de prédominance)

1. [thème principal]
2. [thème secondaire]
3. [...]

#### Décision

- **Selection :** pertinent / non pertinent
- **Catégorie :** A / B / C (si pertinent)
- **Justification :**
  - [argument 1]
  - [argument 2]
  - [...]

---

### Article 2 : [Titre]
[...]
```

---

## 5. Validation

Avant de passer à l'étape suivante, vérifie que :
- [ ] Le fichier `../results/selection_report.md` existe
- [ ] Le fichier `../results/articles_analysis.csv` est complet (toutes les colonnes remplies)
- [ ] Chaque article a une décision (Retenu/Rejeté)
- [ ] Chaque décision a une justification brève mais compréhensible
- [ ] Les articles retenus sont classés par catégorie (A, B ou C)
- [ ] Le résumé en début de fichier est à jour

**Si tout est validé** → Passe à l'étape suivante : `./step6.md`
