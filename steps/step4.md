# Étape 4 : Analyse de pertinence des articles

## 1. Objectif

Analyser chaque article récupéré à l'étape 3 pour déterminer sa **pertinence par rapport à la problématique**.

Cette analyse est faite **par toi** (l'IA), en te basant sur :
- Le **titre** de l'article
- L'**abstract** de l'article
- Les **thèmes identifiés** à l'étape 2 (`../results/themes.json`)

**Fichiers d'entrée :**
- `../results/articles_fetched.md` — Métadonnées des articles
- `../results/themes.json` — Thèmes de référence (primaires, secondaires, voisins)

**Fichier de sortie :**
- `../results/first_analysis.md` — Analyse de pertinence de chaque article

---

## 2. Processus d'analyse

Pour **chaque article**, applique le processus suivant dans l'ordre :

### Étape 4.1 — Analyse du titre

1. Lis le titre de l'article
2. Compare-le aux thèmes du fichier `../results/themes.json`

| Résultat | Action |
|----------|--------|
| Le titre indique clairement que l'article est **hors sujet** | → Rejeter l'article (Selection = `non pertinent`, Justification = `Titre hors sujet`) |
| Le titre suggère un **lien possible** avec la problématique ou le thème de la problématique | → Passer à l'analyse de l'abstract |

### Étape 4.2 — Analyse de l'abstract

1. Lis l'abstract de l'article
2. Identifie les thèmes abordés et compare-les à ceux de l'étape 2

| Résultat | Action |
|----------|--------|
| L'abstract confirme que l'article est **hors sujet** | → Rejeter l'article (Selection = `non pertinent`, Justification = `Abstract hors sujet`) |
| L'abstract confirme une **pertinence potentielle** selon les thèmes du fichier `../results/themes.json` | → Accepter l'article (Selection = `pertinent`, Justification = `Prêt pour analyse approfondie`) |

### Étape 4.3 — Classification par catégorie

Pour les articles retenus, indique à quelle catégorie de thèmes ils correspondent :
- **A. Thème primaire** — Lien direct avec la problématique
- **B. Thème secondaire** — Lien indirect, peut contribuer à la réponse
- **C. Thème voisin** — Même domaine, mais ne répond pas à la problématique

---

## 3. Règles d'analyse

### À faire
- Te baser **uniquement** sur le titre et l'abstract (pas sur tes connaissances externes)
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

Le fichier `../results/first_analysis.md` doit suivre **exactement** ce squelette :

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
- [ ] Le fichier `../results/first_analysis.md` existe
- [ ] Chaque article a été analysé (titre + abstract)
- [ ] Chaque décision est justifiée
- [ ] Les articles retenus sont classés par catégorie (A, B ou C)
- [ ] Le résumé en début de fichier est à jour

**Si tout est validé** → Passe à l'étape suivante : `./step5.md`
