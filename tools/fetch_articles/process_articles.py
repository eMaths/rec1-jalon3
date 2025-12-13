#!/usr/bin/env python3
"""
Script pour récupérer les métadonnées de tous les articles du fichier articles.csv.
Génère articles_metadata.csv et articles_fetched.md dans le dossier results/.
Cette étape ne fait AUCUNE analyse de pertinence.
"""

import csv
import json
import sys
import os
import time

# Ajouter le dossier tools au path pour importer fetch_article
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_article import fetch_article_metadata


def process_articles(input_csv: str, output_csv: str, log_md: str):
    """
    Récupère les métadonnées de tous les articles et génère les fichiers de sortie.
    Cette étape ne fait AUCUNE analyse de pertinence.
    """
    # Lire les articles
    articles = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('doi'):  # Ignorer les lignes sans DOI
                articles.append(row)
    
    print(f"Nombre d'articles à traiter: {len(articles)}")
    
    results = []
    successes = []
    failures = []
    
    for i, article in enumerate(articles):
        doi = article.get('doi', '').strip()
        if not doi:
            continue
            
        print(f"\n[{i+1}/{len(articles)}] Récupération: {doi}")
        
        # Récupérer les métadonnées
        metadata = fetch_article_metadata(doi)
        
        if metadata.get('success'):
            print(f"  ✅ Succès: {metadata.get('title', 'N/A')[:50]}...")
            successes.append(metadata)
        else:
            print(f"  ❌ Erreur: {metadata.get('error', 'Inconnu')}")
            # Utiliser les données du CSV original si disponibles
            metadata['title'] = metadata.get('title') or article.get('title', 'Non disponible')
            metadata['authors'] = metadata.get('authors') or article.get('author', 'Non disponible')
            metadata['journal'] = metadata.get('journal') or article.get('journal', 'Non disponible')
            metadata['year'] = metadata.get('year') or article.get('year', 'Non disponible')
            failures.append(metadata)
        
        results.append(metadata)
        
        # Pause pour ne pas surcharger l'API
        time.sleep(0.5)
    
    # Écrire le CSV de résultats (format step3)
    fieldnames = ['doi', 'title', 'authors', 'abstract', 'journal', 'year', 'keywords', 'fetch_status']
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            status = 'success' if r.get('success') else f"error: {r.get('error', 'Unknown')}"
            writer.writerow({
                'doi': r.get('doi', ''),
                'title': r.get('title', ''),
                'authors': str(r.get('authors', '')).replace(',', ';'),
                'abstract': r.get('abstract', ''),
                'journal': r.get('journal', ''),
                'year': r.get('year', ''),
                'keywords': str(r.get('keywords', '')).replace(',', ';'),
                'fetch_status': status
            })
    
    print(f"\n✅ CSV écrit dans: {output_csv}")
    
    # Écrire le log markdown (format step3)
    with open(log_md, 'w', encoding='utf-8') as f:
        f.write("# Log de récupération des métadonnées\n\n")
        f.write("## Résumé\n\n")
        f.write(f"- **Total d'articles traités :** {len(results)}\n")
        f.write(f"- **Récupérations réussies :** {len(successes)}\n")
        f.write(f"- **Échecs :** {len(failures)}\n\n")
        f.write("---\n\n")
        
        f.write("## Articles récupérés avec succès\n\n")
        for i, r in enumerate(successes, 1):
            f.write(f"### Article {i} : {r.get('title', 'Titre inconnu')}\n\n")
            f.write(f"- **DOI :** {r.get('doi', 'N/A')}\n")
            f.write(f"- **Auteurs :** {r.get('authors', 'N/A')}\n")
            f.write(f"- **Journal :** {r.get('journal', 'N/A')}\n")
            f.write(f"- **Année :** {r.get('year', 'N/A')}\n")
            f.write(f"- **Mots-clés :** {r.get('keywords', 'N/A')}\n")
            f.write(f"- **Abstract :**\n\n")
            f.write(f"> {r.get('abstract', 'Non disponible')}\n\n")
            f.write("---\n\n")
        
        if failures:
            f.write("## Échecs de récupération\n\n")
            f.write("| DOI | Erreur |\n")
            f.write("|-----|--------|\n")
            for r in failures:
                f.write(f"| {r.get('doi', 'N/A')} | {r.get('error', 'Erreur inconnue')} |\n")
    
    print(f"✅ Log écrit dans: {log_md}")
    
    # Résumé
    print(f"\n📊 Résumé:")
    print(f"   - Récupérations réussies: {len(successes)}")
    print(f"   - Échecs: {len(failures)}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    input_csv = os.path.join(base_dir, "data", "articles.csv")
    output_csv = os.path.join(base_dir, "results", "articles_metadata.csv")
    log_md = os.path.join(base_dir, "results", "articles_fetched.md")
    
    # Créer le dossier results s'il n'existe pas
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    process_articles(input_csv, output_csv, log_md)
