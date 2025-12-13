# Étape 4 : Analyse de pertinence des articles

## 1. Objectif

Analyser chaque article récupéré à l'étape 3 pour déterminer sa **pertinence par rapport à la problématique**.

Cette étape se fait en **deux phases** :
1. **Phase A (automatique)** — Pré-filtrage par mots-clés via un script
2. **Phase B (manuelle)** — Validation sémantique par l'agent IA

**Fichiers d'entrée :**
- `../results/articles_fetched.md` — Métadonnées des articles (étape 3)
- `../results/keywords.json` — Mots-clés de référence (étape 2)

**Fichiers de sortie :**
- `../results/candidates.md` — Candidats pré-filtrés (Phase A)
- `../results/final_selection.md` — Sélection finale validée (Phase B)

---

## 2. Phase A : Pré-filtrage automatique

### Commande à exécuter

```bash
python3 ../tools/analyze_articles/analyze_all.py
```

Le script génère `../results/candidates.md` avec :
- Les articles dont le titre ou l'abstract contient des mots-clés de `keywords.json`
- Une catégorie **provisoire** (A, B ou C) basée sur les mots-clés trouvés

⚠️ **IMPORTANT** : Cette liste contient des **faux positifs**. Le script ne peut pas distinguer :
- Un article qui **étudie** le sujet (pertinent)
- Un article qui **utilise** le sujet comme outil (non pertinent)

→ La Phase B est **obligatoire** pour corriger ces erreurs.

---

## 3. Phase B : Validation sémantique par l'agent IA

Pour **chaque article candidat**, tu dois :

### Étape 1 — Lire le titre et l'abstract

Lis attentivement le contenu, pas seulement les mots-clés.

### Étape 2 — Appliquer le Principe 1 (critique)

**Question clé** : L'article **étudie-t-il** le sujet de la problématique, ou **utilise-t-il** ce sujet comme outil pour autre chose ?

| Réponse | Décision |
|---------|----------|
| L'article **étudie, analyse ou améliore** le sujet de la problématique | ✅ Conserver (valider la catégorie A, B ou C) |
| L'article **utilise** le sujet comme outil pour résoudre un autre problème | ❌ Rejeter (marquer comme "faux positif") |

### Étape 3 — Valider ou corriger la catégorie

Si l'article est pertinent, vérifie que la catégorie est correcte :
- **A** — Répond directement à la problématique
- **B** — Contribue indirectement (méthode, métrique, approche réutilisable)
- **C** — Même domaine, potentiellement utile

### Étape 4 — Justifier ta décision

Pour chaque article, écris une justification **sémantique** (pas juste "contient le mot X").

---

## 4. Principes de classification (règles générales)

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

## 5. Règles d'analyse

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

## 6. Format des fichiers de sortie

### 6.1 Fichier `candidates.md` (généré par le script)

Ce fichier est généré automatiquement par le script. Ne pas le modifier.

### 6.2 Fichier `final_selection.md` (généré par l'agent IA)

Le fichier `../results/final_selection.md` doit suivre **exactement** ce squelette :

```markdown
# Sélection finale des articles

## Résumé

- **Candidats analysés :** [nombre]
- **Articles retenus :** [nombre]
- **Faux positifs rejetés :** [nombre]

### Répartition par catégorie

| Catégorie | Nombre |
|-----------|--------|
| A. Lien direct | [nombre] |
| B. Lien indirect | [nombre] |
| C. Même domaine | [nombre] |

---

## Articles retenus

### Article 1 : [Titre]

- **DOI :** [doi]
- **Catégorie :** A / B / C
- **Justification sémantique :** [Explication de pourquoi cet article ÉTUDIE le sujet et non l'utilise comme outil]

---

### Article 2 : [Titre]
[...]

---

## Faux positifs rejetés

### [Titre de l'article rejeté]

- **DOI :** [doi]
- **Catégorie initiale :** A / B / C (attribuée par le script)
- **Raison du rejet :** [Explication de pourquoi cet article UTILISE le sujet comme outil sans l'étudier]

---

### [Autre article rejeté]
[...]
```

---

## 7. Validation

Avant de passer à l'étape suivante, vérifie que :
- [ ] Le fichier `../results/candidates.md` existe (Phase A)
- [ ] Le fichier `../results/final_selection.md` existe (Phase B)
- [ ] Chaque candidat a été relu et validé/rejeté
- [ ] Les faux positifs sont listés avec une justification
- [ ] Les articles retenus ont une justification sémantique (pas juste des mots-clés)

**Si tout est validé** → Passe à l'étape suivante : `./step5.md`
