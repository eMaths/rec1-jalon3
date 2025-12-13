#!/usr/bin/env python3
"""
Parser pour extraire les mots-clés de keywords.json.

Ce fichier est généré par l'agent à l'étape 2 et contient les mots-clés EN
classés en trois catégories : primary, secondary, domain.
"""

import re
import json
from typing import Dict, List, Tuple
from pathlib import Path


def parse_keywords_json(filepath: str) -> Dict:
    """
    Parse le fichier keywords.json et retourne les mots-clés structurés.
    
    Args:
        filepath: Chemin vers le fichier keywords.json
    
    Returns:
        {
            "primary": ["keyword1", "keyword2", ...],
            "secondary": ["keyword1", ...],
            "domain": ["keyword1", ...],
            "all_keywords": ["keyword1", ...]  # Tous les keywords pour matching rapide
        }
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    result = {
        "primary": data.get("primary", []),
        "secondary": data.get("secondary", []),
        "domain": data.get("domain", [])
    }
    
    # Construire la liste de tous les keywords (lowercase pour matching)
    all_keywords = []
    for category in ["primary", "secondary", "domain"]:
        for kw in result[category]:
            all_keywords.append(kw.lower().strip())
    
    result["all_keywords"] = list(set(all_keywords))
    
    return result


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
                "verbs": [{"fr": ..., "en": ...}, ...],
                "nouns": [{"fr": ..., "en": ...}, ...]
            },
            "themes": {
                "primary": [{"theme": ..., "keywords_en": [...], "justification": ...}, ...],
                "secondary": [...],
                "domain": [...]
            },
            "keywords_en": [...]  # All English keywords for matching
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
        elif 'concepts' in section.lower() and ('clés' in section.lower() or 'cles' in section.lower()):
            # Extraire les verbes (format tableau FR/EN)
            verbs_table = extract_concepts_table(section, 'verbes')
            if verbs_table:
                result["concepts"]["verbs"] = verbs_table
            else:
                # Fallback: ancien format liste
                verbs_match = re.search(r'###\s*Verbes?\s*\n((?:[-*]\s*.+\n?)+)', section, re.IGNORECASE)
                if verbs_match:
                    verbs_text = verbs_match.group(1)
                    result["concepts"]["verbs"] = [{"fr": v, "en": v} for v in extract_list_items(verbs_text)]
            
            # Extraire les noms/expressions (format tableau FR/EN)
            nouns_table = extract_concepts_table(section, 'noms')
            if nouns_table:
                result["concepts"]["nouns"] = nouns_table
            else:
                # Fallback: ancien format liste
                nouns_match = re.search(r'###\s*(?:Noms?|Expressions?|Noms?\s*/\s*Expressions?)\s*\n((?:[-*]\s*.+\n?)+)', section, re.IGNORECASE)
                if nouns_match:
                    nouns_text = nouns_match.group(1)
                    result["concepts"]["nouns"] = [{"fr": n, "en": n} for n in extract_list_items(nouns_text)]
        
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
    
    # Construire la liste de tous les keywords EN pour le matching
    result["keywords_en"] = collect_all_english_keywords(result)
    
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


def extract_concepts_table(section: str, concept_type: str) -> List[Dict]:
    """
    Extrait les concepts d'un tableau markdown FR/EN.
    Format attendu: | Français | English |
    """
    concepts = []
    
    # Chercher la sous-section appropriée
    if concept_type.lower() == 'verbes':
        pattern = r'###\s*Verbes?\s*\n'
    else:
        pattern = r'###\s*(?:Noms?|Expressions?|Noms?\s*/\s*Expressions?)\s*\n'
    
    match = re.search(pattern, section, re.IGNORECASE)
    if not match:
        return []
    
    # Extraire le contenu après le header
    start_pos = match.end()
    # Trouver la fin (prochain ### ou fin de section)
    end_match = re.search(r'\n###', section[start_pos:])
    if end_match:
        subsection = section[start_pos:start_pos + end_match.start()]
    else:
        subsection = section[start_pos:]
    
    lines = subsection.split('\n')
    in_table = False
    
    for line in lines:
        line = line.strip()
        
        # Détecter le début du tableau
        if '|' in line and ('français' in line.lower() or 'french' in line.lower() or 'english' in line.lower()):
            in_table = True
            continue
        
        # Ignorer la ligne de séparation
        if in_table and re.match(r'^\|[\s\-:|]+\|$', line):
            continue
        
        # Extraire les données
        if in_table and '|' in line:
            cells = [c.strip() for c in line.split('|')]
            cells = [c for c in cells if c]
            
            if len(cells) >= 2 and cells[0] != '...':
                concepts.append({
                    "fr": cells[0],
                    "en": cells[1]
                })
    
    return concepts


def extract_themes_from_table(section: str) -> List[Dict]:
    """
    Extrait les thèmes d'un tableau markdown.
    Format attendu: | Rang | Thème | Keywords (EN) | Justification |
    Ou ancien format: | Rang | Thème | Justification |
    """
    themes = []
    
    lines = section.split('\n')
    in_table = False
    has_keywords_column = False
    
    for line in lines:
        line = line.strip()
        
        # Détecter le début du tableau et vérifier si colonne Keywords existe
        if '|' in line and ('rang' in line.lower() or 'thème' in line.lower() or 'theme' in line.lower()):
            in_table = True
            has_keywords_column = 'keyword' in line.lower()
            continue
        
        # Ignorer la ligne de séparation
        if in_table and re.match(r'^\|[\s\-:|]+\|$', line):
            continue
        
        # Extraire les données
        if in_table and '|' in line:
            cells = [c.strip() for c in line.split('|')]
            cells = [c for c in cells if c]
            
            if len(cells) >= 2 and cells[0] != '...' and not cells[1].isdigit():
                theme_data = {
                    "theme": cells[1] if len(cells) > 1 else cells[0],
                    "keywords_en": [],
                    "justification": ""
                }
                
                if has_keywords_column and len(cells) >= 3:
                    # Nouveau format avec Keywords (EN)
                    keywords_str = cells[2] if len(cells) > 2 else ""
                    theme_data["keywords_en"] = [k.strip() for k in keywords_str.split(',') if k.strip() and k.strip() != '...']
                    theme_data["justification"] = cells[3] if len(cells) > 3 else ""
                elif len(cells) >= 3:
                    # Ancien format sans Keywords
                    theme_data["justification"] = cells[2]
                
                if theme_data["theme"] and theme_data["theme"] != '...':
                    themes.append(theme_data)
    
    return themes


def collect_all_english_keywords(parsed: Dict) -> List[str]:
    """
    Collecte tous les mots-clés anglais pour le matching avec les articles.
    """
    keywords = []
    
    # Ajouter les keywords EN des thèmes
    for category in ["primary", "secondary", "domain"]:
        for theme in parsed["themes"].get(category, []):
            if isinstance(theme, dict):
                keywords.extend(theme.get("keywords_en", []))
            else:
                # Ancien format: le thème lui-même
                keywords.append(theme)
    
    # Ajouter les concepts EN
    for concept in parsed["concepts"].get("verbs", []):
        if isinstance(concept, dict):
            keywords.append(concept.get("en", ""))
        else:
            keywords.append(concept)
    
    for concept in parsed["concepts"].get("nouns", []):
        if isinstance(concept, dict):
            keywords.append(concept.get("en", ""))
        else:
            keywords.append(concept)
    
    # Nettoyer et dédupliquer
    keywords = [k.lower().strip() for k in keywords if k]
    return list(set(keywords))


def get_all_keywords(parsed: Dict) -> List[str]:
    """
    Retourne tous les mots-clés extraits (thèmes + concepts) pour la recherche.
    Utilise les keywords EN si disponibles.
    """
    return parsed.get("keywords_en", [])


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
