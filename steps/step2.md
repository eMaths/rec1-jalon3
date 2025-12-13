# Étape 2 : Analyse de la problématique

## 1. Objectif

Analyser la problématique pour en extraire les **mots-clés en anglais** qui serviront de critères de sélection des articles scientifiques.

**Fichier d'entrée :** `../data/problematique.md`  
**Fichier de sortie :** `../results/keywords.json`

---

## 2. Méthode d'analyse

### Étape 2.1 — Lecture et compréhension
1. Lis attentivement la problématique
2. Identifie les **concepts clés** (noms, verbes, expressions importantes)

### Étape 2.2 — Extraction des mots-clés EN
**Les articles scientifiques sont en anglais.** Extrais directement les mots-clés en anglais :
- Mots-clés explicites (traduction directe des termes de la problématique)
- Mots-clés implicites (synonymes, termes connexes du domaine)

### Étape 2.3 — Classification en trois catégories

| Catégorie | Description | Critère |
|-----------|-------------|---------|
| **primary** | En lien **direct** avec la problématique | Répondent directement à la question posée |
| **secondary** | En lien **indirect** avec la problématique | Peuvent contribuer à une réponse, même partiellement |
| **domain** | Dans le **domaine général** mais hors problématique | Même champ thématique, sans répondre à la question |

---

## 3. Règles à respecter

### À faire
- Fournir **uniquement des mots-clés en anglais**
- Inclure des **expressions multi-mots** (ex: "energy consumption", "model compression")
- Être **exhaustif** sur les synonymes et variantes
- Respecter **strictement** le format JSON

### À ne pas faire
- Ajouter des explications ou justifications dans le JSON
- Inclure des mots-clés en français
- Ajouter des champs non demandés

---

## 4. Format du fichier de sortie

Le fichier `../results/keywords.json` doit suivre **exactement** ce schéma JSON :

```json
{
  "primary": [
    "keyword1",
    "keyword2",
    "multi-word expression",
    ...
  ],
  "secondary": [
    "keyword1",
    "keyword2",
    ...
  ],
  "domain": [
    "keyword1",
    "keyword2",
    ...
  ]
}
```

### Exemple concret

Pour une problématique sur "l'efficacité énergétique des modèles ML" :

```json
{
  "primary": [
    "energy efficiency",
    "energy-efficient",
    "energy consumption",
    "power consumption",
    "green AI",
    "sustainable AI",
    "energy optimization",
    "power optimization",
    "energy-aware",
    "low-power"
  ],
  "secondary": [
    "model compression",
    "pruning",
    "quantization",
    "knowledge distillation",
    "lightweight model",
    "efficient architecture",
    "carbon footprint",
    "edge computing",
    "hardware-aware"
  ],
  "domain": [
    "machine learning",
    "deep learning",
    "neural network",
    "cloud computing",
    "data center"
  ]
}
```

---

## 5. Validation

Avant de passer à l'étape suivante, vérifie que :
- [ ] Le fichier `../results/keywords.json` existe
- [ ] Le JSON est valide (pas d'erreur de syntaxe)
- [ ] Les trois catégories sont présentes
- [ ] Tous les mots-clés sont en anglais

**Si tout est validé** → Passe à l'étape suivante : `./step3.md`
