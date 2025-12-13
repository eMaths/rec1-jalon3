#!/usr/bin/env python3
"""Outil one-shot pour récupérer TOUS les abstracts des articles.
Usage: python3 fetch_all.py

Lit articles.csv et génère:
- results/articles_metadata.csv
- results/articles_fetched.md (articles avec abstracts complets)
- results/missing_abstracts.md (articles sans abstract, à compléter manuellement)
"""

import csv
import os
import sys
import time
from datetime import datetime

# Ajouter le dossier courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_article import fetch_article_metadata, is_valid_abstract


def fetch_all_articles():
    """
    Récupère tous les articles et génère les fichiers de sortie.
    """
    # Chemins
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    input_csv = os.path.join(base_dir, "data", "articles.csv")
    results_dir = os.path.join(base_dir, "results")
    output_csv = os.path.join(results_dir, "articles_metadata.csv")
    output_md = os.path.join(results_dir, "articles_fetched.md")
    missing_md = os.path.join(results_dir, "missing_abstracts.md")
    
    # Créer le dossier results
    os.makedirs(results_dir, exist_ok=True)
    
    print("=" * 60)
    print("🚀 FETCH ALL ARTICLES - One Shot")
    print("=" * 60)
    print(f"📁 Input:  {input_csv}")
    print(f"📁 Output: {results_dir}/")
    print("=" * 60)
    
    # Lire les articles
    articles = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('doi'):
                articles.append(row)
    
    total = len(articles)
    print(f"\n📊 {total} articles à traiter\n")
    
    # Récupérer les métadonnées
    results = []
    valid_abstracts = []
    invalid_abstracts = []
    
    start_time = time.time()
    
    for i, article in enumerate(articles):
        doi = article.get('doi', '').strip()
        if not doi:
            continue
        
        print(f"[{i+1}/{total}] {doi[:50]}...", end=" ", flush=True)
        
        metadata = fetch_article_metadata(doi)
        
        if metadata.get('success'):
            if metadata.get('abstract_valid'):
                print(f"✅ ({metadata.get('abstract_length', 0)} chars)")
                valid_abstracts.append(metadata)
            else:
                print(f"⚠️ (abstract incomplet)")
                invalid_abstracts.append(metadata)
        else:
            print(f"❌ Erreur")
            invalid_abstracts.append(metadata)
        
        results.append(metadata)
        time.sleep(0.3)  # Rate limiting
    
    elapsed = time.time() - start_time
    
    # Écrire le CSV
    fieldnames = ['doi', 'title', 'authors', 'abstract', 'journal', 'year', 
                  'keywords', 'abstract_valid', 'abstract_length', 'source']
    
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                'doi': r.get('doi', ''),
                'title': r.get('title', ''),
                'authors': str(r.get('authors', '')).replace(',', ';'),
                'abstract': r.get('abstract', ''),
                'journal': r.get('journal', ''),
                'year': r.get('year', ''),
                'keywords': str(r.get('keywords', '')).replace(',', ';'),
                'abstract_valid': r.get('abstract_valid', False),
                'abstract_length': r.get('abstract_length', 0),
                'source': r.get('source', '')
            })
    
    # Écrire le Markdown
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write("# Articles - Métadonnées et Abstracts\n\n")
        f.write(f"*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        # Résumé
        f.write("## 📊 Résumé\n\n")
        f.write(f"| Métrique | Valeur |\n")
        f.write(f"|----------|--------|\n")
        f.write(f"| Total articles | {total} |\n")
        f.write(f"| Abstracts complets | {len(valid_abstracts)} ✅ |\n")
        f.write(f"| Abstracts manquants | {len(invalid_abstracts)} ⚠️ |\n")
        f.write(f"| Taux de succès | {len(valid_abstracts)/total*100:.1f}% |\n")
        f.write(f"| Temps d'exécution | {elapsed:.1f}s |\n\n")
        
        # Sources
        sources = {}
        for r in results:
            src = r.get('source', 'Unknown')
            sources[src] = sources.get(src, 0) + 1
        
        f.write("### Sources utilisées\n\n")
        for src, count in sorted(sources.items(), key=lambda x: -x[1]):
            f.write(f"- **{src}**: {count}\n")
        f.write("\n---\n\n")
        
        # Tous les articles avec abstracts complets
        f.write("## 📚 Articles avec abstracts complets\n\n")
        for i, r in enumerate(valid_abstracts, 1):
            f.write(f"### {i}. {r.get('title', 'Sans titre')}\n\n")
            f.write(f"- **DOI**: `{r.get('doi')}`\n")
            f.write(f"- **Auteurs**: {r.get('authors', 'N/A')}\n")
            f.write(f"- **Journal**: {r.get('journal', 'N/A')}\n")
            f.write(f"- **Année**: {r.get('year', 'N/A')}\n")
            f.write(f"- **Mots-clés**: {r.get('keywords', 'N/A')}\n")
            f.write(f"- **Source**: {r.get('source', 'N/A')}\n\n")
            f.write(f"**Abstract** ({r.get('abstract_length', 0)} caractères):\n\n")
            f.write(f"> {r.get('abstract', 'Non disponible')}\n\n")
            f.write("---\n\n")
        
    # Générer le fichier des abstracts manquants
    if invalid_abstracts:
        with open(missing_md, 'w', encoding='utf-8') as f:
            f.write("# Articles sans abstract\n\n")
            f.write(f"*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write(f"**{len(invalid_abstracts)} article(s)** nécessitent une intervention manuelle.\n\n")
            f.write("## Instructions\n\n")
            f.write("1. Pour chaque article ci-dessous, ouvrez le lien DOI\n")
            f.write("2. Copiez l'abstract depuis la page de l'article\n")
            f.write("3. Collez-le à l'emplacement indiqué (remplacez `[COLLER L'ABSTRACT ICI]`)\n")
            f.write("4. Une fois terminé, informez l'agent IA pour continuer\n\n")
            f.write("---\n\n")
            
            for i, r in enumerate(invalid_abstracts, 1):
                f.write(f"### Article {i} : {r.get('title', 'Sans titre')}\n\n")
                f.write(f"- **DOI :** `{r.get('doi')}`\n")
                f.write(f"- **Lien :** https://doi.org/{r.get('doi')}\n")
                f.write(f"- **Auteurs :** {r.get('authors', 'N/A')}\n")
                f.write(f"- **Journal :** {r.get('journal', 'N/A')}\n")
                f.write(f"- **Année :** {r.get('year', 'N/A')}\n\n")
                f.write("**Abstract (à compléter) :**\n\n")
                f.write("> [COLLER L'ABSTRACT ICI]\n\n")
                f.write("---\n\n")
    
    # Résumé final
    print("\n" + "=" * 60)
    print("✅ TERMINÉ")
    print("=" * 60)
    print(f"📊 Résultats:")
    print(f"   - Abstracts complets: {len(valid_abstracts)}/{total} ({len(valid_abstracts)/total*100:.1f}%)")
    print(f"   - Abstracts manquants: {len(invalid_abstracts)}/{total}")
    print(f"   - Temps: {elapsed:.1f}s")
    print(f"\n📁 Fichiers générés:")
    print(f"   - {output_csv}")
    print(f"   - {output_md}")
    if invalid_abstracts:
        print(f"   - {missing_md}")
        print("\n" + "=" * 60)
        print(f"⚠️  ATTENTION : {len(invalid_abstracts)} article(s) sans abstract !")
        print("=" * 60)
        print(f"\nVeuillez compléter le fichier : {missing_md}")
        print("\nPour chaque article listé :")
        print("  1. Ouvrez le lien DOI dans votre navigateur")
        print("  2. Copiez l'abstract depuis la page de l'article")
        print("  3. Collez-le dans le fichier à l'emplacement indiqué")
        print("\nUne fois terminé, dites \"c'est fait\" à l'agent IA.")
    print("=" * 60)


if __name__ == "__main__":
    fetch_all_articles()
