# Étape 3 : Récupération des métadonnées des articles

## 1. Objectif

Récupérer les **métadonnées complètes** de chaque article listé dans le fichier d'entrée. 

**Cette étape ne fait AUCUNE analyse de pertinence.** Tu récupères uniquement les données brutes.

**Fichier d'entrée :** `../data/articles.csv`  
**Fichiers de sortie :**
- `../results/articles_metadata.csv` — Données structurées de tous les articles
- `../results/articles_fetched.md` — Log détaillé du processus de récupération

---

## 2. Commande à exécuter

```bash
python3 ../tools/fetch_articles/fetch_all.py
```

---

## 3. Fichier de sortie

Le script génère `../results/articles_fetched.md` qui contient :

1. **Résumé** — Statistiques globales (nombre d'articles, taux de succès)
2. **Articles avec abstracts complets** — Pour chaque article :
   - Titre, DOI, auteurs, journal, année, mots-clés
   - Abstract complet en citation
3. **Articles avec abstracts manquants** — Liste des articles sans abstract récupérable

**C'est ce fichier que tu utiliseras à l'étape 4** pour analyser la pertinence de chaque article.

---

## 4. Validation

Avant de passer à l'étape suivante, vérifie que :
- [ ] Le fichier `../results/articles_metadata.csv` existe et contient tous les articles
- [ ] Le fichier `../results/articles_fetched.md` existe avec le résumé et le détail
- [ ] Chaque article a un statut (succès ou erreur documentée)
- [ ] Les données essentielles (titre, abstract, auteurs) sont présentes pour les succès

**Si tout est validé** → Passe à l'étape suivante : `./step4.md`

