# Projet : Classification d'articles scientifiques pour une revue systématique

# Etape 1 : Prendre connaissance du projet et des consignes

## 1. Objectif principal

Tu es un assistant IA chargé de **classifier et trier des articles scientifiques** selon un processus méthodologique strict et reproductible.

**But final :** Produire une sélection d'articles pertinents pour répondre à la problématique de recherche définie dans `../data/problematique.md`.

---

## 2. Structure du projet

| Dossier/Fichier | Description |
|-----------------|-------------|
| `./steps/` | Étapes du processus (fichiers Markdown numérotés) |
| `../data/` | Données d'entrée (articles.csv, problematique.md) |
| `../tools/` | Scripts Python pour automatiser certaines tâches |
| `../results/` | **Seul dossier où tu peux écrire** — tes fichiers de sortie |

---

## 3. Règles de fonctionnement

### 3.1 Permissions
- ❌ **Interdit** : Modifier les fichiers du projet (steps, data, tools)
- ✅ **Autorisé** : Créer et modifier des fichiers uniquement dans `../results/`
- ✅ **Autorisé** : Créer le dossier `../results/` s'il n'existe pas

### 3.2 Méthodologie
- **Suis les étapes dans l'ordre** : step1.md → step2.md → ...
- **Exécute exactement ce qui est demandé** : ni plus, ni moins
- **Conserve les fichiers produits** : chaque étape peut réutiliser les sorties des étapes précédentes
- **Reproductibilité** : ta méthode doit donner le même résultat si appliquée par une autre personne ou IA

### 3.3 Communication
- **En cas de doute** : pose une question claire et précise avant d'agir
- **En cas de blocage** : décris le problème exact pour qu'on le résolve ensemble
- **Préfère demander** plutôt que de faire des suppositions incorrectes
- **Tout le temps** justifie tes choix, tes actions, ce que tu écris dans des fichiers markdown

---

## 4. Ressources disponibles

### Données d'entrée
- `../data/articles.csv` — Liste des articles à analyser (DOI, métadonnées)
- `../data/problematique.md` — Problématique de recherche à laquelle les articles doivent répondre

### Outils
- `../tools/fetch_articles/` — Scripts pour récupérer les métadonnées d'articles via leur DOI
- `../tools/pdf_to_markdown/` — Scripts pour convertir des PDF en Markdown

Les outils seront présentés en détail dans les étapes concernées.

---

## 5. Démarrage

**Prérequis avant de continuer :**
1. As-tu compris l'objectif du projet ?
2. As-tu des questions sur les règles ou la structure ?

**Si tout est clair** → Passe directement à l'étape suivante, pas besoin de m'interroger ou me le proposer: `./step2.md`