# Processus de sélection

Tu trouveras la problématique dans ../data/problematique.md

Pour la problématique, il faut fournir une analyse de la problématique et identifier 2 choses : 
- l'ensemble des sujets et mot clés en parfait alignement avec la problématiques, le thèmes en lien indirect.
- l'ensemble des sujets et mot clés qui peuvent être en lien avec la problématiques, le thèmes en lien indirect ou thèmes secondaires AUTOUR de la problématique.

Avant de commencer preparer un nouveau csv, `result.csv` dans ../results/ lequel tu mettras les colonnes suivantes :

```text
Selection	title	abstract	author	journal	Issue type	year	doi	keywords justification
```

1. Pour chaque article du fichier ../data/articles.csv, récupère le lien dans la colonne "doi".

> Grâce à ce lien, tu récupères deux choses : le titre de l'article ainsi que l'abstract
> Les liens, le nom de l'article et les auteurs tu vas les mettre dans un fichier markdown  `../results/article_fetch_log.md` pour me permettre de suivre ton processus et m'assurer que tu fetch les bonnes données, pour chaque article tu mets le titre, les auteurs, le lien, le doi, et l'abstract, les raisons de pourquoi l'article est pertinent et les raisons de pourquoi l'article n'est pas pertinent.

Pour les justifications tu dois expliquer si l'article est TRES pertinent en lien direct ou pourquoi il l'est quand même mais de façon indirecte et pourquoi il pourrait servir comme élément de réponse à la problématique.

le format exigé pour chaque article est le suivant : 

```markdown
## Article: Titre de l'article
- Auteurs: Liste des auteurs
- Lien: [DOI](https://doi.org/lien_doi)
- Abstract: Résumé de l'article
- themes abordés dans l'article (classé par ordre "principalement abordé"): 
    - theme1
    - theme2
    - theme3

- Article retenu ? True/False
- Raisons : 
    - arg1
    - arg2
    - arg3
```

## Analyse du titre

Lire le titre de l’article.


### 1. Si le titre indique clairement que l’article n’est pas lié au sujet cible :

> Rejeter l’article, cela veut dire que tu mets "non pertinent" dans la colonne "Selection" et tu mets "Titre non pertinent" dans la colonne "justification".

Arrêter le traitement de cette source et passe à la suivante.
---

### 2. Sinon (le titre suggère un lien possible avec le sujet) :

Passer à l’étape suivante.
---


### 2. Analyse du résumé (abstract)

Lire l’abstract de l’article.

### 1. Si l’abstract indique que l’article n’est pas pertinent pour le sujet :

Rejeter l’article, cela veut dire que tu mets "non pertinent" dans la colonne "Selection" et tu mets "Abstract non pertinent" dans la colonne "justification".

Arrêter le traitement de cette source et passe à la suivante.

#### 2. Sinon (l’abstract confirme une pertinence potentielle) :

Tu acceptes l'article, cela veut dire que tu mets "pertinent" dans la colonne "Selection" et tu mets "Prêt pour analyse de l'article" dans la colonne "justification". 