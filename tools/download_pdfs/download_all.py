#!/usr/bin/env python3
"""
Télécharge tous les PDFs des articles sélectionnés.

Usage:
    python download_all.py

Fichiers d'entrée:
    - ../results/final_selection.md (ou candidates.md si final_selection n'existe pas)

Fichiers de sortie:
    - ../results/pdfs/ (dossier contenant les PDFs)
    - ../results/download_report.md (rapport de téléchargement)
    - ../results/unavailable_articles.md (articles non accessibles)
"""

import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# Ajouter le dossier courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from download_pdf import download_pdf, check_accessibility, _normalize_doi


def parse_selection_file(filepath: Path) -> list[dict]:
    """
    Parse le fichier de sélection pour extraire les DOIs.
    Supporte candidates.md et final_selection.md
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    articles = []
    
    # Pattern pour extraire les articles
    # Format: ### Article N : Titre ou ### Titre
    article_sections = re.split(r'(?=###\s+(?:Article\s*\d+\s*:|[^#]))', content)
    
    for section in article_sections:
        if not section.strip():
            continue
        
        # Extraire le titre
        title_match = re.search(r'###\s*(?:Article\s*\d+\s*:)?\s*(.+?)(?=\n)', section)
        if not title_match:
            continue
        title = title_match.group(1).strip()
        
        # Ignorer les sections non-articles
        if title.lower() in ['résumé', 'summary', 'faux positifs rejetés', 'articles retenus']:
            continue
        
        # Extraire le DOI
        doi_match = re.search(r'\*\*DOI\s*[:\*]*\s*`?([^`\n]+)`?', section, re.IGNORECASE)
        if not doi_match:
            continue
        doi = doi_match.group(1).strip()
        doi = _normalize_doi(doi)
        
        if not doi:
            continue
        
        # Extraire la catégorie si présente
        cat_match = re.search(r'\*\*Catégorie\s*[:\*]*\s*([ABC])', section, re.IGNORECASE)
        category = cat_match.group(1) if cat_match else "?"
        
        # Vérifier si c'est un article retenu (pas rejeté)
        is_rejected = 'non pertinent' in section.lower() or 'faux positif' in section.lower()
        
        if not is_rejected:
            articles.append({
                'title': title,
                'doi': doi,
                'category': category
            })
    
    return articles


def main():
    # Chemins
    base_dir = Path(__file__).parent.parent.parent
    results_dir = base_dir / "results"
    pdfs_dir = results_dir / "pdfs"
    
    # Fichiers d'entrée (priorité à final_selection.md)
    final_selection = results_dir / "final_selection.md"
    candidates = results_dir / "candidates.md"
    
    if final_selection.exists():
        input_file = final_selection
    elif candidates.exists():
        input_file = candidates
    else:
        print("❌ Aucun fichier de sélection trouvé!")
        print(f"   Attendu: {final_selection} ou {candidates}")
        return 1
    
    # Fichiers de sortie
    report_file = results_dir / "download_report.md"
    unavailable_file = results_dir / "unavailable_articles.md"
    
    print("=" * 60)
    print("📥 TÉLÉCHARGEMENT DES PDFs")
    print("=" * 60)
    print(f"📁 Entrée: {input_file}")
    print(f"📁 Sortie: {pdfs_dir}/")
    print("=" * 60)
    
    # Parser le fichier de sélection
    articles = parse_selection_file(input_file)
    print(f"\n📊 {len(articles)} articles à télécharger\n")
    
    if not articles:
        print("⚠️ Aucun article trouvé dans le fichier de sélection")
        return 1
    
    # Créer le dossier de sortie
    pdfs_dir.mkdir(parents=True, exist_ok=True)
    
    # Télécharger les PDFs
    downloaded = []
    unavailable = []
    
    start_time = time.time()
    
    for i, article in enumerate(articles, 1):
        doi = article['doi']
        title = article['title'][:50] + "..." if len(article['title']) > 50 else article['title']
        
        print(f"[{i}/{len(articles)}] {title}")
        print(f"         DOI: {doi}")
        
        success, message, path = download_pdf(doi, pdfs_dir)
        
        if success:
            print(f"         ✅ {message}")
            downloaded.append({
                **article,
                'path': str(path),
                'source': message.replace("Téléchargé depuis ", "")
            })
        else:
            print(f"         ❌ {message}")
            
            # Vérifier l'accessibilité pour plus de détails
            accessible, sources = check_accessibility(doi)
            unavailable.append({
                **article,
                'reason': message,
                'sources_found': sources
            })
        
        print()
    
    elapsed = time.time() - start_time
    
    # Générer le rapport
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Rapport de téléchargement des PDFs\n\n")
        f.write(f"*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        f.write("## Résumé\n\n")
        f.write(f"| Métrique | Valeur |\n")
        f.write(f"|----------|--------|\n")
        f.write(f"| Total articles | {len(articles)} |\n")
        f.write(f"| PDFs téléchargés | {len(downloaded)} ✅ |\n")
        f.write(f"| Non accessibles | {len(unavailable)} ❌ |\n")
        f.write(f"| Taux de succès | {len(downloaded)/len(articles)*100:.1f}% |\n")
        f.write(f"| Temps d'exécution | {elapsed:.1f}s |\n\n")
        
        f.write("---\n\n")
        
        f.write("## PDFs téléchargés\n\n")
        if downloaded:
            f.write("| # | Titre | DOI | Source |\n")
            f.write("|---|-------|-----|--------|\n")
            for i, art in enumerate(downloaded, 1):
                title_short = art['title'][:40] + "..." if len(art['title']) > 40 else art['title']
                f.write(f"| {i} | {title_short} | `{art['doi']}` | {art['source']} |\n")
        else:
            f.write("*Aucun PDF téléchargé*\n")
        
        f.write("\n---\n\n")
        
        f.write("## Articles non accessibles\n\n")
        if unavailable:
            f.write("Ces articles nécessitent un accès manuel (bibliothèque, achat, etc.)\n\n")
            for i, art in enumerate(unavailable, 1):
                f.write(f"### {i}. {art['title']}\n\n")
                f.write(f"- **DOI:** `{art['doi']}`\n")
                f.write(f"- **Lien:** https://doi.org/{art['doi']}\n")
                f.write(f"- **Raison:** {art['reason']}\n\n")
        else:
            f.write("*Tous les articles ont été téléchargés avec succès!*\n")
    
    # Générer le fichier des articles non accessibles
    if unavailable:
        with open(unavailable_file, 'w', encoding='utf-8') as f:
            f.write("# Articles non accessibles\n\n")
            f.write(f"*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write(f"**{len(unavailable)} article(s)** nécessitent un accès manuel.\n\n")
            f.write("## Instructions\n\n")
            f.write("Pour chaque article ci-dessous :\n")
            f.write("1. Accédez au lien DOI\n")
            f.write("2. Téléchargez le PDF via votre accès institutionnel ou achetez l'article\n")
            f.write("3. Placez le PDF dans le dossier `results/pdfs/`\n")
            f.write("4. Nommez le fichier avec le DOI (remplacez `/` par `_`)\n\n")
            f.write("---\n\n")
            
            for i, art in enumerate(unavailable, 1):
                f.write(f"### Article {i} : {art['title']}\n\n")
                f.write(f"- **DOI:** `{art['doi']}`\n")
                f.write(f"- **Lien:** https://doi.org/{art['doi']}\n")
                f.write(f"- **Catégorie:** {art['category']}\n\n")
                f.write("**PDF (à ajouter manuellement):**\n\n")
                f.write(f"Nom de fichier attendu: `{art['doi'].replace('/', '_')}.pdf`\n\n")
                f.write("---\n\n")
    
    # Résumé final
    print("=" * 60)
    print("✅ TÉLÉCHARGEMENT TERMINÉ")
    print("=" * 60)
    print(f"📊 Résultats:")
    print(f"   - PDFs téléchargés: {len(downloaded)}/{len(articles)}")
    print(f"   - Non accessibles: {len(unavailable)}/{len(articles)}")
    print(f"   - Temps: {elapsed:.1f}s")
    print(f"\n📁 Fichiers générés:")
    print(f"   - {pdfs_dir}/ ({len(downloaded)} PDFs)")
    print(f"   - {report_file}")
    if unavailable:
        print(f"   - {unavailable_file}")
        print(f"\n⚠️  ATTENTION: {len(unavailable)} article(s) non accessibles!")
        print(f"    Veuillez compléter manuellement: {unavailable_file}")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
