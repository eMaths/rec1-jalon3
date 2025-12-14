# Étape 2 : Analyse de la problématique

## 1. Objectif

Analyser la problématique pour en extraire les **thèmes et mots-clés** qui serviront de critères de sélection des articles dans les étapes suivantes.

**Fichier d'entrée :** `../data/problematique.md`  
**Fichiers de sortie :**
- `../results/analyse_problematique.md` — Analyse détaillée avec justifications
- `../results/themes.json` — Liste structurée des thèmes pour le filtrage automatique

---

## 2. Méthode d'analyse

### Étape 2.1 — Lecture et reformulation
1. Lis attentivement la problématique
2. Identifie les **concepts clés** (noms, verbes, expressions importantes)
3. Reformule la problématique en une phrase simple pour vérifier ta compréhension

### Étape 2.2 — Extraction des termes
Extrais une liste de **verbes** et **noms** en lien avec la problématique :
- Termes explicitement présents dans la problématique
- Termes implicites ou synonymes

### Étape 2.3 — Classification des thèmes
Classe les thèmes identifiés en **trois catégories distinctes** :

| Catégorie | Description | Critère |
|-----------|-------------|---------|
| **A. Thèmes primaires** | En lien **direct** avec la problématique | Répondent directement à la question posée |
| **B. Thèmes secondaires** | En lien **indirect** avec la problématique | Peuvent contribuer à une réponse, même partiellement |
| **C. Thèmes voisins** | Dans le **domaine général** mais hors problématique | Même champ thématique, sans répondre à la question |

**Pour chaque catégorie :**
- Classe les thèmes **par ordre de pertinence décroissante**
- Justifie brièvement pourquoi chaque thème est dans cette catégorie

---

## 3. Règles à respecter

### À faire
- Rester focalisé sur les thèmes **pertinents ou potentiellement pertinents**
- Justifier chaque choix de manière **concise et factuelle**
- Être **pédagogue** : un lecteur externe doit comprendre ton raisonnement
- Accepter les thèmes du même domaine qui pourraient contribuer à la réponse

### À ne pas faire
- Lister des thèmes **hors sujet** (sans lien avec la problématique)
- Faire des paragraphes trop longs ou du remplissage
- Ajouter des schémas ou diagrammes
- Lister des thèmes "non pertinents" ou "hors sujet" — **on ne cite que les thèmes pertinents**

> **Principe de filtrage :** Tout article qui correspond à un des thèmes listés (primaires, secondaires ou voisins) sera retenu. Les autres seront exclus. Il n'y a pas de catégorie "non pertinent" à définir.

---

## 4. Format du fichier de sortie

Le fichier `../results/analyse_problematique.md` doit suivre **exactement** ce squelette :

```markdown
# Analyse de la problématique

## 1. Problématique originale

> [Copier ici la problématique telle qu'elle apparaît dans le fichier source]

## 2. Reformulation

[Une phrase simple qui résume la problématique dans tes propres mots]

## 3. Concepts clés extraits

### Verbes
- [verbe1]
- [verbe2]
- ...

### Noms / Expressions
- [nom1]
- [nom2]
- ...

## 4. Thèmes primaires (lien direct)

| Rang | Thème | Justification |
|------|-------|---------------|
| 1 | [thème] | [pourquoi ce thème répond directement à la problématique] |
| 2 | [thème] | [justification] |
| ... | ... | ... |

## 5. Thèmes secondaires (lien indirect)

| Rang | Thème | Justification |
|------|-------|---------------|
| 1 | [thème] | [pourquoi ce thème pourrait contribuer à la réponse] |
| 2 | [thème] | [justification] |
| ... | ... | ... |

## 6. Thèmes voisins (même domaine, hors problématique)

| Rang | Thème | Justification |
|------|-------|---------------|
| 1 | [thème] | [pourquoi ce thème est dans le domaine mais ne répond pas à la problématique] |
| 2 | [thème] | [justification] |
| ... | ... | ... |

## 7. Synthèse

[2-3 phrases résumant les critères de sélection qui seront utilisés pour filtrer les articles]
```

---

## 5. Validation

Avant de passer à l'étape suivante, vérifie que :
- [ ] Le fichier `../results/analyse_problematique.md` existe
- [ ] Le fichier `../results/themes.json` existe et est valide
- [ ] Les trois catégories de thèmes sont bien distinctes
- [ ] Chaque thème a une justification
- [ ] Aucun thème "non pertinent" ou "hors sujet" n'est listé
- [ ] Le raisonnement est compréhensible par un lecteur externe

---

## 6. Fichier JSON de sortie

En plus du fichier Markdown, génère un fichier `../results/themes.json` avec la structure suivante :

```json
{
  "themes_primaires": ["themeLePlusPertinent", "deuxiemeThemePlusPertinent", "..."],
  "themes_secondaires": ["themeLePlusPertinent", "deuxiemeThemePlusPertinent", "..."],
  "themes_voisins": ["themeLePlusPertinent", "deuxiemeThemePlusPertinent", "..."]
}
```

**Règles :**
- Les thèmes sont classés **par ordre de pertinence décroissante** dans chaque liste
- Utiliser les mêmes noms de thèmes que dans le fichier Markdown
- Ce fichier servira au filtrage automatique des articles dans les étapes suivantes

---

**Si tout est validé** → Passe à l'étape suivante : `./step3.md`