#!/usr/bin/env python3
"""
Orchestrateur principal pour l'analyse de pertinence des articles.

Usage:
    python3 analyze_all.py

Fichiers d'entrée (générés aux étapes précédentes):
    - ../results/analyse_problematique.md (étape 2)
    - ../results/articles_fetched.md (étape 3)

Fichier de sortie:
    - ../results/first_analysis.md (étape 4)
"""

import os
import sys
import re
import json
from datetime import datetime
from typing import Dict, List

# Ajouter le dossier courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parse_problematique import parse_analyse_problematique
from analyze_title import analyze_title
from analyze_abstract import analyze_abstract


def parse_articles_fetched(filepath: str) -> List[Dict]:
    """
    Parse le fichier articles_fetched.md pour extraire les articles.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    articles = []
    
    # Chercher tous les articles (format: ### N. Titre ou ### Article N : Titre)
    article_pattern = r'###\s*(?:\d+\.|Article\s*\d+\s*:)\s*(.+?)(?=\n)'
    article_sections = re.split(r'(?=###\s*(?:\d+\.|Article\s*\d+\s*:))', content)
    
    for section in article_sections:
        if not section.strip():
            continue
        
        # Extraire le titre
        title_match = re.search(r'###\s*(?:\d+\.|Article\s*\d+\s*:)\s*(.+?)(?=\n)', section)
        if not title_match:
            continue
        
        title = title_match.group(1).strip()
        
        # Extraire le DOI
        doi_match = re.search(r'\*\*DOI\s*[:\*]*\s*`?([^`\n]+)`?', section, re.IGNORECASE)
        doi = doi_match.group(1).strip() if doi_match else ""
        
        # Extraire les auteurs
        authors_match = re.search(r'\*\*Auteurs?\s*[:\*]*\s*(.+?)(?=\n)', section, re.IGNORECASE)
        authors = authors_match.group(1).strip() if authors_match else ""
        
        # Extraire le journal
        journal_match = re.search(r'\*\*Journal\s*[:\*]*\s*(.+?)(?=\n)', section, re.IGNORECASE)
        journal = journal_match.group(1).strip() if journal_match else ""
        
        # Extraire l'année
        year_match = re.search(r'\*\*Ann[ée]e\s*[:\*]*\s*(\d{4})', section, re.IGNORECASE)
        year = year_match.group(1) if year_match else ""
        
        # Extraire l'abstract (après > ou **Abstract**)
        abstract = ""
        abstract_match = re.search(r'(?:\*\*Abstract\*\*[^>]*>\s*|>\s*)(.+?)(?=\n---|\n###|\Z)', section, re.DOTALL | re.IGNORECASE)
        if abstract_match:
            abstract = abstract_match.group(1).strip()
            # Nettoyer les > en début de ligne
            abstract = re.sub(r'^>\s*', '', abstract, flags=re.MULTILINE)
            abstract = abstract.strip()
        
        if title and title != "..." and not title.startswith("["):
            articles.append({
                "title": title,
                "doi": doi,
                "authors": authors,
                "journal": journal,
                "year": year,
                "abstract": abstract
            })
    
    return articles


def analyze_article(article: Dict, themes: Dict, concepts: Dict) -> Dict:
    """
    Analyse un article complet (titre + abstract).
    """
    title = article.get("title", "")
    abstract = article.get("abstract", "")
    
    # Étape 1: Analyse du titre
    title_result = analyze_title(title, themes, concepts)
    
    # Étape 2: Analyse de l'abstract (si le titre n'a pas été rejeté)
    if title_result["decision"] == "reject":
        return {
            "article": article,
            "title_analysis": title_result,
            "abstract_analysis": None,
            "final_decision": "reject",
            "final_category": None,
            "final_reason": title_result["reason"],
            "themes_identified": [],
            "confidence": title_result["confidence"]
        }
    
    abstract_result = analyze_abstract(abstract, themes, concepts, title_result)
    
    return {
        "article": article,
        "title_analysis": title_result,
        "abstract_analysis": abstract_result,
        "final_decision": abstract_result["decision"],
        "final_category": abstract_result["category"],
        "final_reason": abstract_result["reason"],
        "themes_identified": abstract_result["themes_identified"],
        "confidence": abstract_result["confidence"]
    }


def generate_output_markdown(results: List[Dict], parsed_problematique: Dict) -> str:
    """
    Génère le fichier de sortie first_analysis.md.
    """
    # Compter les résultats
    total = len(results)
    accepted = [r for r in results if r["final_decision"] == "accept"]
    rejected = [r for r in results if r["final_decision"] == "reject"]
    
    cat_a = [r for r in accepted if r["final_category"] == "A"]
    cat_b = [r for r in accepted if r["final_category"] == "B"]
    cat_c = [r for r in accepted if r["final_category"] == "C"]
    
    output = []
    output.append("# Analyse de pertinence des articles\n")
    output.append(f"*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    # Résumé
    output.append("\n## Résumé\n")
    output.append(f"- **Total d'articles analysés :** {total}")
    output.append(f"- **Articles retenus (pertinents) :** {len(accepted)}")
    output.append(f"- **Articles rejetés (non pertinents) :** {len(rejected)}\n")
    
    output.append("### Répartition des articles retenus par catégorie\n")
    output.append("| Catégorie | Nombre |")
    output.append("|-----------|--------|")
    output.append(f"| A. Thèmes primaires | {len(cat_a)} |")
    output.append(f"| B. Thèmes secondaires | {len(cat_b)} |")
    output.append(f"| C. Thèmes voisins | {len(cat_c)} |")
    
    output.append("\n---\n")
    
    # Articles analysés
    output.append("## Articles analysés\n")
    
    for i, result in enumerate(results, 1):
        article = result["article"]
        
        output.append(f"### Article {i} : {article['title']}\n")
        output.append(f"- **Auteurs :** {article.get('authors', 'N/A')}")
        output.append(f"- **DOI :** {article.get('doi', 'N/A')}")
        if article.get('doi'):
            output.append(f"- **Lien :** https://doi.org/{article['doi']}")
        
        output.append("\n#### Abstract\n")
        abstract = article.get('abstract', 'Non disponible')
        if abstract and abstract != "Non disponible":
            output.append(f"> {abstract[:500]}{'...' if len(abstract) > 500 else ''}\n")
        else:
            output.append("> *Abstract non disponible*\n")
        
        output.append("#### Thèmes identifiés (par ordre de prédominance)\n")
        themes_identified = result.get("themes_identified", [])
        if themes_identified:
            for j, theme in enumerate(themes_identified[:5], 1):
                output.append(f"{j}. {theme}")
        else:
            output.append("1. Aucun thème identifié")
        
        output.append("\n#### Décision\n")
        decision = "pertinent" if result["final_decision"] == "accept" else "non pertinent"
        output.append(f"- **Selection :** {decision}")
        
        if result["final_category"]:
            output.append(f"- **Catégorie :** {result['final_category']}")
        
        output.append(f"- **Confiance :** {result['confidence']:.0%}")
        output.append("- **Justification :**")
        output.append(f"  - {result['final_reason']}")
        
        # Ajouter les détails des correspondances
        if result.get("abstract_analysis"):
            matched = result["abstract_analysis"].get("matched_themes", {})
            if matched.get("primary"):
                output.append(f"  - Thèmes primaires trouvés: {', '.join(matched['primary'])}")
            if matched.get("secondary"):
                output.append(f"  - Thèmes secondaires trouvés: {', '.join(matched['secondary'])}")
            if matched.get("domain"):
                output.append(f"  - Thèmes du domaine trouvés: {', '.join(matched['domain'])}")
        
        output.append("\n---\n")
    
    return "\n".join(output)


def main():
    """
    Point d'entrée principal.
    """
    # Chemins
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    results_dir = os.path.join(base_dir, "results")
    
    problematique_file = os.path.join(results_dir, "analyse_problematique.md")
    articles_file = os.path.join(results_dir, "articles_fetched.md")
    output_file = os.path.join(results_dir, "first_analysis.md")
    
    print("=" * 60)
    print("🔍 ANALYSE DE PERTINENCE DES ARTICLES")
    print("=" * 60)
    
    # Vérifier les fichiers d'entrée
    if not os.path.exists(problematique_file):
        print(f"❌ Fichier non trouvé: {problematique_file}")
        print("   → Exécutez d'abord l'étape 2 pour générer analyse_problematique.md")
        sys.exit(1)
    
    if not os.path.exists(articles_file):
        print(f"❌ Fichier non trouvé: {articles_file}")
        print("   → Exécutez d'abord l'étape 3 (python3 fetch_all.py)")
        sys.exit(1)
    
    # Parser la problématique
    print(f"\n📖 Lecture de {problematique_file}...")
    parsed = parse_analyse_problematique(problematique_file)
    
    themes = parsed["themes"]
    concepts = parsed["concepts"]
    
    print(f"   Thèmes primaires: {len(themes.get('primary', []))}")
    print(f"   Thèmes secondaires: {len(themes.get('secondary', []))}")
    print(f"   Thèmes du domaine: {len(themes.get('domain', []))}")
    print(f"   Concepts (verbes + noms): {len(concepts.get('verbs', [])) + len(concepts.get('nouns', []))}")
    
    # Parser les articles
    print(f"\n📚 Lecture de {articles_file}...")
    articles = parse_articles_fetched(articles_file)
    print(f"   {len(articles)} articles trouvés")
    
    # Analyser chaque article
    print(f"\n🔬 Analyse en cours...")
    results = []
    
    for i, article in enumerate(articles, 1):
        print(f"   [{i}/{len(articles)}] {article['title'][:50]}...", end=" ")
        result = analyze_article(article, themes, concepts)
        results.append(result)
        
        status = "✅" if result["final_decision"] == "accept" else "❌"
        cat = f"({result['final_category']})" if result["final_category"] else ""
        print(f"{status} {cat}")
    
    # Générer le fichier de sortie
    print(f"\n📝 Génération de {output_file}...")
    output_content = generate_output_markdown(results, parsed)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    # Résumé final
    accepted = len([r for r in results if r["final_decision"] == "accept"])
    rejected = len([r for r in results if r["final_decision"] == "reject"])
    
    print("\n" + "=" * 60)
    print("✅ ANALYSE TERMINÉE")
    print("=" * 60)
    print(f"📊 Résultats:")
    print(f"   - Articles retenus: {accepted}/{len(results)}")
    print(f"   - Articles rejetés: {rejected}/{len(results)}")
    print(f"\n📁 Fichier généré: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
