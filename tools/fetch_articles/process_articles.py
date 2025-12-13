#!/usr/bin/env python3
"""
Script pour récupérer les métadonnées de tous les articles du fichier articles.csv.
Génère articles_metadata.csv et articles_fetched.md dans le dossier results/.
Version améliorée avec meilleure récupération des abstracts via multiples sources.
Cette étape ne fait AUCUNE analyse de pertinence.
"""

import csv
import json
import sys
import os
import time

# Ajouter le dossier tools au path pour importer fetch_article
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_article import fetch_article_metadata, is_valid_abstract


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
    valid_abstracts = []
    invalid_abstracts = []
    
    for i, article in enumerate(articles):
        doi = article.get('doi', '').strip()
        if not doi:
            continue
            
        print(f"\n[{i+1}/{len(articles)}] Récupération: {doi}")
        
        # Récupérer les métadonnées
        metadata = fetch_article_metadata(doi)
        
        if metadata.get('success'):
            abstract_status = "✅" if metadata.get('abstract_valid') else "⚠️"
            abstract_len = metadata.get('abstract_length', 0)
            print(f"  ✅ Succès: {metadata.get('title', 'N/A')[:50]}...")
            print(f"     Abstract: {abstract_status} ({abstract_len} caractères) - Source: {metadata.get('source', 'N/A')}")
            successes.append(metadata)
            
            # Tracker les abstracts valides/invalides
            if metadata.get('abstract_valid'):
                valid_abstracts.append(metadata)
            else:
                invalid_abstracts.append(metadata)
        else:
            print(f"  ❌ Erreur: {metadata.get('error', 'Inconnu')}")
            # Utiliser les données du CSV original si disponibles
            metadata['title'] = metadata.get('title') or article.get('title', 'Non disponible')
            metadata['authors'] = metadata.get('authors') or article.get('author', 'Non disponible')
            metadata['journal'] = metadata.get('journal') or article.get('journal', 'Non disponible')
            metadata['year'] = metadata.get('year') or article.get('year', 'Non disponible')
            failures.append(metadata)
            invalid_abstracts.append(metadata)
        
        results.append(metadata)
        
        # Pause pour ne pas surcharger l'API
        time.sleep(0.5)
    
    # Écrire le CSV de résultats (format step3)
    fieldnames = ['doi', 'title', 'authors', 'abstract', 'journal', 'year', 'keywords', 'fetch_status', 'abstract_valid', 'abstract_length', 'source']
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
                'fetch_status': status,
                'abstract_valid': r.get('abstract_valid', False),
                'abstract_length': r.get('abstract_length', 0),
                'source': r.get('source', '')
            })
    
    print(f"\n✅ CSV écrit dans: {output_csv}")
    
    # Écrire le log markdown (format step3)
    with open(log_md, 'w', encoding='utf-8') as f:
        f.write("# Log de récupération des métadonnées\n\n")
        f.write("## Résumé\n\n")
        f.write(f"- **Total d'articles traités :** {len(results)}\n")
        f.write(f"- **Récupérations réussies :** {len(successes)}\n")
        f.write(f"- **Échecs :** {len(failures)}\n")
        f.write(f"- **Abstracts valides (complets) :** {len(valid_abstracts)} ✅\n")
        f.write(f"- **Abstracts manquants/incomplets :** {len(invalid_abstracts)} ⚠️\n\n")
        
        # Statistiques par source
        sources_count = {}
        for r in successes:
            src = r.get('source', 'Unknown')
            sources_count[src] = sources_count.get(src, 0) + 1
        
        f.write("### Sources utilisées\n\n")
        for src, count in sorted(sources_count.items(), key=lambda x: -x[1]):
            f.write(f"- **{src}**: {count} articles\n")
        f.write("\n---\n\n")
        
        # Articles avec abstracts valides
        f.write("## Articles avec abstracts complets ✅\n\n")
        for i, r in enumerate(valid_abstracts, 1):
            f.write(f"### {i}. {r.get('title', 'Titre inconnu')}\n\n")
            f.write(f"- **DOI :** `{r.get('doi', 'N/A')}`\n")
            f.write(f"- **Auteurs :** {r.get('authors', 'N/A')}\n")
            f.write(f"- **Journal :** {r.get('journal', 'N/A')}\n")
            f.write(f"- **Année :** {r.get('year', 'N/A')}\n")
            f.write(f"- **Mots-clés :** {r.get('keywords', 'N/A')}\n")
            f.write(f"- **Source :** {r.get('source', 'N/A')}\n")
            f.write(f"- **Longueur abstract :** {r.get('abstract_length', 0)} caractères\n\n")
            f.write(f"**Abstract :**\n\n")
            f.write(f"> {r.get('abstract', 'Non disponible')}\n\n")
            f.write("---\n\n")
        
        # Articles avec abstracts manquants/incomplets
        if invalid_abstracts:
            f.write("## Articles avec abstracts manquants ou incomplets ⚠️\n\n")
            for i, r in enumerate(invalid_abstracts, 1):
                f.write(f"### {i}. {r.get('title', 'Titre inconnu')}\n\n")
                f.write(f"- **DOI :** `{r.get('doi', 'N/A')}`\n")
                f.write(f"- **Auteurs :** {r.get('authors', 'N/A')}\n")
                f.write(f"- **Journal :** {r.get('journal', 'N/A')}\n")
                f.write(f"- **Année :** {r.get('year', 'N/A')}\n")
                f.write(f"- **Source :** {r.get('source', 'N/A')}\n")
                f.write(f"- **Sources essayées :** {', '.join(r.get('sources_tried', []))}\n")
                abstract = r.get('abstract', 'Non disponible')
                if abstract and abstract != 'Non disponible':
                    f.write(f"- **Abstract partiel ({len(abstract)} caractères) :**\n\n")
                    f.write(f"> {abstract}\n\n")
                else:
                    f.write(f"- **Abstract :** Non disponible\n\n")
                f.write("---\n\n")
        
        if failures:
            f.write("## Échecs de récupération ❌\n\n")
            f.write("| DOI | Erreur |\n")
            f.write("|-----|--------|\n")
            for r in failures:
                f.write(f"| `{r.get('doi', 'N/A')}` | {r.get('error', 'Erreur inconnue')} |\n")
    
    print(f"✅ Log écrit dans: {log_md}")
    
    # Résumé
    print(f"\n📊 Résumé:")
    print(f"   - Récupérations réussies: {len(successes)}")
    print(f"   - Abstracts valides: {len(valid_abstracts)} ✅")
    print(f"   - Abstracts manquants/incomplets: {len(invalid_abstracts)} ⚠️")
    print(f"   - Échecs: {len(failures)}")
    
    # Taux de succès des abstracts
    if len(results) > 0:
        abstract_rate = (len(valid_abstracts) / len(results)) * 100
        print(f"   - Taux d'abstracts complets: {abstract_rate:.1f}%")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    input_csv = os.path.join(base_dir, "data", "articles.csv")
    output_csv = os.path.join(base_dir, "results", "articles_metadata.csv")
    log_md = os.path.join(base_dir, "results", "articles_fetched.md")
    
    # Créer le dossier results s'il n'existe pas
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    process_articles(input_csv, output_csv, log_md)
