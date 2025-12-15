# Workflow d'Analyse et Classification d'Articles Scientifiques

## Instructions pour l'Assistant IA

Ce document décrit le workflow complet pour analyser et classifier des articles scientifiques en fonction d'une problématique de recherche. Suivez ces instructions étape par étape.

---

## Prérequis

L'utilisateur doit fournir :
1. **Une problématique de recherche** clairement définie
2. **Une liste d'articles** avec au minimum :
   - DOI
   - Titre
   - Abstract (résumé)

---

## Étape 1 : Analyse de la problématique

### 1.1 Identifier les éléments clés

À partir de la problématique, extraire :

```markdown
## Concepts clés de la problématique

### Verbes d'action
- [verbe 1] (ex: concevoir, évaluer, réduire, optimiser)
- [verbe 2]
- ...

### Noms/Expressions clés
- [concept 1] (ex: modèles d'apprentissage automatique)
- [concept 2] (ex: consommation d'énergie)
- ...

### Thèmes primaires (lien direct)
1. [Thème 1] - [Justification]
2. [Thème 2] - [Justification]
...

### Thèmes secondaires (lien indirect)
1. [Thème 1] - [Justification]
2. [Thème 2] - [Justification]
...
```

### 1.2 Définir le critère de sélection principal

Formuler une règle claire de type :

```
Un article est PERTINENT si : [condition principale]
Un article est NON PERTINENT si : [condition d'exclusion]
```

**Exemple** :
- ✅ Pertinent : L'article traite de l'efficacité énergétique DU modèle ML lui-même
- ❌ Non pertinent : L'article utilise le ML POUR optimiser l'énergie d'autre chose

---

## Étape 2 : Définir la grille d'évaluation

### 2.1 Questions de filtrage (4-5 questions)

Créer des questions binaires (Oui/Non) pour évaluer chaque article :

```markdown
| # | Question | Réponse attendue |
|---|----------|------------------|
| Q1 | L'article traite-t-il de [concept principal] ? | Oui/Non |
| Q2 | L'article aborde-t-il [aspect clé 1] ? | Oui/Non |
| Q3 | L'article propose-t-il [aspect clé 2] ? | Oui/Non |
| Q4 | L'article mesure-t-il [aspect clé 3] ? | Oui/Non |
```

### 2.2 Règle de décision

```markdown
**Règle de décision** :
- Q1=Oui ET (Q2=Oui OU Q3=Oui OU Q4=Oui) → 🟢 PERTINENT
- Q1=Oui ET Q2-Q4=Non mais domaine connexe → 🟡 PARTIELLEMENT PERTINENT
- Q1=Non OU [condition d'exclusion] → 🔴 NON PERTINENT
```

### 2.3 Motifs d'exclusion standardisés

Définir les motifs d'exclusion possibles :

```markdown
| Motif | Description |
|-------|-------------|
| `hors scope` | [Description spécifique à la problématique] |
| `non pertinent` | Pas de lien avec le sujet principal |
| `inaccessible` | Abstract non disponible (langue, accès) |
| `source secondaire` | Review sans contribution originale |
| `trop spécifique` | Domaine trop éloigné |
```

### 2.4 Code couleur

```markdown
| Couleur | Signification | Action |
|---------|---------------|--------|
| 🟢 Vert | Pertinent | À garder pour analyse approfondie |
| 🟡 Jaune | Partiellement pertinent | À discuter / garder pour contexte |
| 🔴 Rouge | Non pertinent | À exclure |
```

---

## Étape 3 : Traitement des articles

### 3.1 Pour chaque article, produire :

```markdown
### Article [N] : [Titre court]
- **DOI** : [doi]
- **Année** : [année]
- **Résumé condensé** : [80-150 mots résumant l'abstract]
- **Évaluation** :
  - Q1 : [Oui/Non] - [commentaire bref]
  - Q2 : [Oui/Non] - [commentaire bref]
  - Q3 : [Oui/Non] - [commentaire bref]
  - Q4 : [Oui/Non] - [commentaire bref]
- **Décision** : 🟢/🟡/🔴
- **Justification** : [1-2 phrases expliquant pourquoi garder ou exclure]
- **Motif si exclu** : [motif standardisé]
```

### 3.2 Traitement par lots recommandé

1. **Option A** : Traiter 5 articles d'abord comme exemple, valider les critères avec l'utilisateur
2. **Option B** : Traiter par lots de 10 articles pour validation intermédiaire
3. **Option C** : Traiter tous les articles d'un coup si les critères sont clairs

---

## Étape 4 : Génération des livrables

### 4.1 Fichier Excel avec 4 feuilles

#### Feuille 1 : "Articles issus de la chaine"
| Colonne | Description |
|---------|-------------|
| N° | Numéro de l'article |
| Titre | Titre complet |
| Résumé | Abstract condensé en français |
| DOI | Identifiant DOI |
| Année | Année de publication |
| Auteurs | (optionnel) |
| Journal | (optionnel) |
| Mots-clés | (optionnel) |

#### Feuille 2 : "Selection"
| Colonne | Description |
|---------|-------------|
| N° | Numéro de l'article |
| Titre | Titre complet |
| Décision | pertinent / partiellement pertinent / [motif d'exclusion] |
| Justification | Explication factuelle |
| DOI | Identifiant DOI |

**Appliquer le code couleur** :
- Lignes vertes : articles pertinents
- Lignes jaunes : articles partiellement pertinents
- Lignes rouges : articles non pertinents

#### Feuille 3 : "Analyse"
Uniquement pour les articles 🟢 pertinents :

| Colonne | Description |
|---------|-------------|
| N° | Numéro de l'article |
| Titre | Titre court |
| Résumé | Abstract condensé |
| Critère 1 | [Selon la problématique] |
| Critère 2 | [Selon la problématique] |
| Critère 3 | [Selon la problématique] |
| ... | ... |
| DOI | Identifiant DOI |

#### Feuille 4 : "Légende"
- Explication des codes couleurs
- Explication des critères d'analyse
- Liste des motifs d'exclusion

### 4.2 Fichier Markdown de synthèse

Structure du document :

```markdown
# Analyse et Sélection des [N] Articles

## Problématique de recherche
> [Problématique complète]

### Critère de sélection principal
[Règle de sélection]

---

## Résumé statistique
| Catégorie | Nombre | Pourcentage |
|-----------|--------|-------------|
| 🟢 Pertinents | X | X% |
| 🟡 Partiellement pertinents | X | X% |
| 🔴 Non pertinents | X | X% |

---

## 🟢 Articles pertinents (X articles)
[Pour chaque article : DOI, année, résumé, résultats clés, justification]

---

## 🟡 Articles partiellement pertinents (X articles)
[Pour chaque article : DOI, résumé bref, raison du classement partiel]

---

## 🔴 Articles non pertinents (X articles)
[Classés par catégorie d'exclusion avec tableau récapitulatif]

---

## Synthèse pour la présentation
- Points clés à retenir
- Distinction fondamentale
- Métriques rencontrées
- Recommandations
```

---

## Étape 5 : Validation avec l'utilisateur

### 5.1 Points de validation

1. **Après l'analyse de la problématique** : Valider les critères de sélection
2. **Après les 5 premiers articles** : Ajuster les critères si nécessaire
3. **Après la classification complète** : Revoir les cas limites (🟡)

### 5.2 Questions à poser à l'utilisateur

- "Êtes-vous d'accord avec la distinction [pertinent] vs [non pertinent] ?"
- "Voulez-vous garder les articles [catégorie] comme contexte ou les exclure ?"
- "Y a-t-il des critères supplémentaires à ajouter ?"

---

## Template de critères d'analyse (Feuille "Analyse")

Adapter selon la problématique. Exemples de critères génériques :

| Critère | Description | Valeurs possibles |
|---------|-------------|-------------------|
| Type de contribution | Nature de l'apport | New model / Existing model / Modification |
| Focus | Phase du ML concernée | Entraînement / Inférence / Les deux |
| Technique | Méthode utilisée | Compression / Architecture / Hardware / Autre |
| Validation | Type de validation | Expérimentale / Théorique / Simulation |
| Domaine | Champ d'application | Général / Spécifique (préciser) |
| Type de recherche | Nature de l'article | Validation / Evaluation / Solution / Opinion |

---

## Checklist finale

- [ ] Problématique analysée et critères définis
- [ ] Grille d'évaluation créée (questions + règle de décision)
- [ ] Tous les articles traités et classifiés
- [ ] Fichier Excel généré avec 4 feuilles
- [ ] Code couleur appliqué
- [ ] Fichier Markdown de synthèse généré
- [ ] Validation avec l'utilisateur effectuée

---

## Exemple d'utilisation

**Entrée utilisateur** :
```
Problématique : "Comment concevoir des modèles ML plus durables en réduisant leur consommation d'énergie ?"

Articles : [liste de 45 articles avec DOI et abstracts]
```

**Sortie attendue** :
1. `Tableau_analyse_[N]_articles.xlsx` - Fichier Excel complet
2. `analyse_selection_articles.md` - Document de synthèse
3. Récapitulatif dans le chat avec statistiques et articles clés

---

## Notes importantes

1. **Toujours justifier factuellement** : Chaque décision doit être basée sur le contenu de l'abstract, pas sur des suppositions.

2. **Résumer, ne pas copier** : Les abstracts doivent être condensés en français (80-150 mots).

3. **Être cohérent** : Appliquer les mêmes critères à tous les articles.

4. **Documenter les cas limites** : Les articles 🟡 doivent avoir une justification claire de leur statut intermédiaire.

5. **Adapter les critères** : Les critères d'analyse (Feuille 3) doivent être adaptés à chaque problématique.
