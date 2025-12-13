#!/usr/bin/env python3
"""
Parser pour extraire les thèmes et concepts de analyse_problematique.md.

Ce fichier est généré par l'agent à l'étape 2 et suit un format structuré.
Le parser extrait :
- La problématique originale
- La reformulation
- Les concepts clés (verbes et noms)
- Les thèmes primaires, secondaires et voisins
"""

import re
from typing import Dict, List, Tuple
from pathlib import Path


def parse_analyse_problematique(filepath: str) -> Dict:
    """
    Parse le fichier analyse_problematique.md et extrait les informations structurées.
    
    Args:
        filepath: Chemin vers le fichier analyse_problematique.md
    
    Returns:
        {
            "problematique": str,
            "reformulation": str,
            "concepts": {
                "verbs": [...],
                "nouns": [...]
            },
            "themes": {
                "primary": [...],
                "secondary": [...],
                "domain": [...]
            },
            "synthese": str
        }
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = {
        "problematique": "",
        "reformulation": "",
        "concepts": {
            "verbs": [],
            "nouns": []
        },
        "themes": {
            "primary": [],
            "secondary": [],
            "domain": []
        },
        "synthese": ""
    }
    
    # Diviser en sections
    sections = re.split(r'^## \d+\.', content, flags=re.MULTILINE)
    
    for section in sections:
        section = section.strip()
        
        # Section: Problématique originale
        if section.lower().startswith('problématique originale') or section.lower().startswith('problematique originale'):
            # Extraire le contenu entre > (citation)
            match = re.search(r'>\s*(.+?)(?:\n\n|\Z)', section, re.DOTALL)
            if match:
                result["problematique"] = match.group(1).strip()
        
        # Section: Reformulation
        elif section.lower().startswith('reformulation'):
            lines = section.split('\n')
            # Prendre tout après le titre de section
            content_lines = [l.strip() for l in lines[1:] if l.strip() and not l.startswith('#')]
            result["reformulation"] = ' '.join(content_lines)
        
        # Section: Concepts clés extraits
        elif 'concepts' in section.lower() and 'clés' in section.lower():
            # Extraire les verbes
            verbs_match = re.search(r'###\s*Verbes?\s*\n((?:[-*]\s*.+\n?)+)', section, re.IGNORECASE)
            if verbs_match:
                verbs_text = verbs_match.group(1)
                result["concepts"]["verbs"] = extract_list_items(verbs_text)
            
            # Extraire les noms/expressions
            nouns_match = re.search(r'###\s*(?:Noms?|Expressions?|Noms?\s*/\s*Expressions?)\s*\n((?:[-*]\s*.+\n?)+)', section, re.IGNORECASE)
            if nouns_match:
                nouns_text = nouns_match.group(1)
                result["concepts"]["nouns"] = extract_list_items(nouns_text)
        
        # Section: Thèmes primaires
        elif 'thèmes primaires' in section.lower() or 'themes primaires' in section.lower():
            result["themes"]["primary"] = extract_themes_from_table(section)
        
        # Section: Thèmes secondaires
        elif 'thèmes secondaires' in section.lower() or 'themes secondaires' in section.lower():
            result["themes"]["secondary"] = extract_themes_from_table(section)
        
        # Section: Thèmes voisins
        elif 'thèmes voisins' in section.lower() or 'themes voisins' in section.lower():
            result["themes"]["domain"] = extract_themes_from_table(section)
        
        # Section: Synthèse
        elif section.lower().startswith('synthèse') or section.lower().startswith('synthese'):
            lines = section.split('\n')
            content_lines = [l.strip() for l in lines[1:] if l.strip() and not l.startswith('#')]
            result["synthese"] = ' '.join(content_lines)
    
    return result


def extract_list_items(text: str) -> List[str]:
    """
    Extrait les éléments d'une liste markdown (- item ou * item).
    """
    items = []
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('-') or line.startswith('*'):
            item = line.lstrip('-*').strip()
            if item:
                items.append(item)
    return items


def extract_themes_from_table(section: str) -> List[str]:
    """
    Extrait les thèmes d'un tableau markdown.
    Format attendu: | Rang | Thème | Justification |
    """
    themes = []
    
    # Chercher les lignes du tableau
    lines = section.split('\n')
    in_table = False
    
    for line in lines:
        line = line.strip()
        
        # Détecter le début du tableau
        if '|' in line and ('rang' in line.lower() or 'thème' in line.lower() or 'theme' in line.lower()):
            in_table = True
            continue
        
        # Ignorer la ligne de séparation (|---|---|---|)
        if in_table and re.match(r'^\|[\s\-:|]+\|$', line):
            continue
        
        # Extraire les données du tableau
        if in_table and '|' in line:
            cells = [c.strip() for c in line.split('|')]
            # Filtrer les cellules vides
            cells = [c for c in cells if c]
            
            if len(cells) >= 2:
                # La deuxième colonne contient le thème
                theme = cells[1] if len(cells) > 1 else cells[0]
                # Ignorer si c'est juste un numéro ou vide
                if theme and not theme.isdigit() and theme != '...':
                    themes.append(theme)
    
    return themes


def get_all_keywords(parsed: Dict) -> List[str]:
    """
    Retourne tous les mots-clés extraits (thèmes + concepts) pour la recherche.
    """
    keywords = []
    
    # Ajouter les thèmes
    for category in ["primary", "secondary", "domain"]:
        keywords.extend(parsed["themes"].get(category, []))
    
    # Ajouter les concepts
    keywords.extend(parsed["concepts"].get("verbs", []))
    keywords.extend(parsed["concepts"].get("nouns", []))
    
    return keywords


if __name__ == "__main__":
    import sys
    import json
    
    # Test avec un fichier
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # Chemin par défaut
        filepath = "../../results/analyse_problematique.md"
    
    try:
        result = parse_analyse_problematique(filepath)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {filepath}")
        print("Usage: python parse_problematique.py <chemin_vers_analyse_problematique.md>")
