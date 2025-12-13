# Étape 4 : Analyse de pertinence des articles

## 1. Objectif

Analyser chaque article récupéré à l'étape 3 pour déterminer sa **pertinence par rapport à la problématique**.

Cette analyse est faite **par toi** (l'IA), en te basant sur :
- Le **titre** de l'article
- L'**abstract** de l'article
- Les **thèmes identifiés** à l'étape 2 (`../results/analyse_problematique.md`)

**Fichiers d'entrée :**
- `../results/articles_fetched.md` — Métadonnées des articles
- `../results/analyse_problematique.md` — Thèmes de référence (primaires, secondaires, voisins)

**Fichier de sortie :**
- `../results/first_analysis.md` — Analyse de pertinence de chaque article

---

## 2. Processus d'analyse

Pour **chaque article**, applique le processus suivant dans l'ordre :

### Étape 4.1 — Analyse du titre

1. Lis le titre de l'article
2. Compare-le aux thèmes identifiés à l'étape 2

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
| L'abstract confirme une **pertinence potentielle** selon les thèmes identifiés à l'étape 2 dans le fichier `../results/analyse_problematique.md` | → Accepter l'article (Selection = `pertinent`, Justification = `Prêt pour analyse approfondie`) |

### Étape 4.3 — Classification par catégorie

Pour les articles retenus, indique à quelle catégorie de thèmes ils correspondent :
- **A. Thème primaire** — Lien direct avec la problématique
- **B. Thème secondaire** — Lien indirect, peut contribuer à la réponse
- **C. Thème voisin** — Même domaine, mais ne répond pas directement à la problématique

---

## 3. Principes de classification (règles générales)

### Principe 1 : Distinguer "étudier le sujet" vs "utiliser le sujet comme outil"

La problématique porte sur **l'étude ou l'amélioration d'un sujet X**. Il faut distinguer :

| Type d'article | Classification |
|----------------|----------------|
| L'article **étudie, analyse ou améliore** le sujet X lui-même | ✅ Pertinent (A, B ou C) |
| L'article **utilise** le sujet X comme outil pour résoudre un autre problème | ❌ Hors sujet |

**Exemple générique :**
- Si la problématique porte sur "améliorer les performances des voitures électriques"
  - ✅ "Optimisation des batteries pour véhicules électriques" → Pertinent (étudie le sujet)
  - ❌ "Utilisation de voitures électriques pour livrer des colis" → Hors sujet (utilise le sujet comme outil)

### Principe 2 : Accepter les éléments de réponse indirects (Catégorie B)

Un article est en **catégorie B** s'il :
- Traite d'un aspect **connexe** au sujet principal
- Pourrait fournir une **méthode, métrique ou approche** réutilisable
- Aborde un **sous-problème** de la problématique

**Exemple générique :**
- Problématique : "Comment réduire la consommation d'énergie de X ?"
- Article : "Méthodes de mesure de performance pour X" → **Catégorie B** (fournit des outils d'évaluation)

### Principe 3 : Garder les thèmes voisins du même domaine (Catégorie C)

Un article est en **catégorie C** s'il :
- Appartient au **même domaine scientifique** que la problématique
- Ne répond pas directement à la question posée
- Pourrait **potentiellement** être utile dans une perspective plus large

**Exemple générique :**
- Problématique : "Comment optimiser l'algorithme Y ?"
- Article : "Nouvelle technique d'échantillonnage pour algorithmes similaires à Y" → **Catégorie C** (même domaine, potentiellement transférable)

### Principe 4 : Rejeter uniquement les articles clairement hors domaine

Un article est **hors sujet** uniquement s'il :
- N'a **aucun lien** avec le domaine de la problématique
- Traite d'un **champ d'application** sans rapport avec l'étude du sujet

**Exemple générique :**
- Problématique : "Comment améliorer la technique X ?"
- Article : "Application de X pour résoudre un problème dans un domaine totalement différent" → **Hors sujet**

---

## 4. Règles d'analyse

### À faire
- Te baser **uniquement** sur le titre et l'abstract (pas sur tes connaissances externes)
- Justifier **chaque décision** avec des arguments concrets
- Lister les thèmes abordés dans l'article par ordre de prédominance
- Être **cohérent** avec les thèmes définis à l'étape 2
- **Être inclusif** : en cas de doute, préférer garder l'article en catégorie B ou C plutôt que de le rejeter

### À ne pas faire
- Accepter un article sans justification
- Rejeter un article sans explication claire
- Inventer des informations non présentes dans le titre/abstract
- Modifier les fichiers d'entrée
- **Être trop restrictif** : ne pas rejeter un article simplement parce qu'il n'est pas en lien direct

---

## 5. Format du fichier de sortie

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

## 6. Validation

Avant de passer à l'étape suivante, vérifie que :
- [ ] Le fichier `../results/first_analysis.md` existe
- [ ] Chaque article a été analysé (titre + abstract)
- [ ] Chaque décision est justifiée
- [ ] Les articles retenus sont classés par catégorie (A, B ou C)
- [ ] Le résumé en début de fichier est à jour

**Si tout est validé** → Passe à l'étape suivante : `./step5.md`
