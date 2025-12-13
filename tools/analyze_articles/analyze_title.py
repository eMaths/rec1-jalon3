#!/usr/bin/env python3
"""
Analyse du titre d'un article par rapport aux thèmes extraits de analyse_problematique.md.

Règles (basées sur step4.md) :
- Si le titre indique CLAIREMENT que l'article est hors sujet → rejeter
- Si le titre suggère un lien POSSIBLE avec la problématique → passer à l'abstract

Principe clé : Distinguer "étudier le sujet" vs "utiliser le sujet comme outil"
"""

import re
from typing import Dict, List


def analyze_title(title: str, themes: Dict[str, List[str]], concepts: Dict[str, List[str]]) -> Dict:
    """
    Analyse le titre d'un article par rapport aux thèmes extraits.
    
    Args:
        title: Le titre de l'article
        themes: Dict avec clés "primary", "secondary", "domain" contenant les thèmes
        concepts: Dict avec clés "verbs", "nouns" contenant les concepts clés
    
    Returns:
        {
            "decision": "continue" | "reject",
            "confidence": float (0-1),
            "matched_themes": {"primary": [...], "secondary": [...], "domain": [...]},
            "matched_concepts": [...],
            "reason": str
        }
    """
    title_lower = title.lower()
    
    matched_themes = {
        "primary": [],
        "secondary": [],
        "domain": []
    }
    matched_concepts = []
    
    # Chercher les correspondances avec les thèmes
    for category in ["primary", "secondary", "domain"]:
        for theme in themes.get(category, []):
            # Chercher le thème ou ses mots individuels
            theme_lower = theme.lower()
            theme_words = [w for w in theme_lower.split() if len(w) > 3]
            
            # Match exact du thème
            if theme_lower in title_lower:
                matched_themes[category].append(theme)
            # Match partiel (au moins 2 mots du thème)
            elif len(theme_words) >= 2:
                matches = sum(1 for w in theme_words if w in title_lower)
                if matches >= 2 or (matches >= 1 and len(theme_words) == 1):
                    matched_themes[category].append(theme)
            # Match d'un mot significatif
            elif len(theme_words) == 1 and theme_words[0] in title_lower:
                matched_themes[category].append(theme)
    
    # Chercher les correspondances avec les concepts (verbes et noms)
    all_concepts = concepts.get("verbs", []) + concepts.get("nouns", [])
    for concept in all_concepts:
        concept_lower = concept.lower()
        if len(concept_lower) > 3 and concept_lower in title_lower:
            matched_concepts.append(concept)
    
    # Calculer les scores
    primary_score = len(matched_themes["primary"])
    secondary_score = len(matched_themes["secondary"])
    domain_score = len(matched_themes["domain"])
    concept_score = len(matched_concepts)
    
    # Logique de décision
    
    # Règle 1: Thèmes primaires trouvés → très probablement pertinent
    if primary_score >= 1:
        return {
            "decision": "continue",
            "confidence": 0.9,
            "matched_themes": matched_themes,
            "matched_concepts": matched_concepts,
            "reason": f"Titre correspond à {primary_score} thème(s) primaire(s): {matched_themes['primary']}"
        }
    
    # Règle 2: Thèmes secondaires trouvés → probablement pertinent
    if secondary_score >= 1:
        return {
            "decision": "continue",
            "confidence": 0.7,
            "matched_themes": matched_themes,
            "matched_concepts": matched_concepts,
            "reason": f"Titre correspond à {secondary_score} thème(s) secondaire(s): {matched_themes['secondary']}"
        }
    
    # Règle 3: Thèmes du domaine trouvés → à vérifier avec l'abstract
    if domain_score >= 1:
        return {
            "decision": "continue",
            "confidence": 0.5,
            "matched_themes": matched_themes,
            "matched_concepts": matched_concepts,
            "reason": f"Titre dans le même domaine: {matched_themes['domain']}"
        }
    
    # Règle 4: Concepts clés trouvés → à vérifier avec l'abstract
    if concept_score >= 2:
        return {
            "decision": "continue",
            "confidence": 0.5,
            "matched_themes": matched_themes,
            "matched_concepts": matched_concepts,
            "reason": f"Titre contient {concept_score} concepts clés: {matched_concepts}"
        }
    
    # Règle 5: Aucune correspondance → continuer quand même (être inclusif)
    # On ne rejette PAS sur le titre seul (principe d'inclusivité du step4)
    return {
        "decision": "continue",
        "confidence": 0.3,
        "matched_themes": matched_themes,
        "matched_concepts": matched_concepts,
        "reason": "Aucune correspondance directe, vérification de l'abstract nécessaire"
    }


if __name__ == "__main__":
    # Test avec des thèmes simulés
    themes = {
        "primary": ["efficacité énergétique", "consommation d'énergie", "Green AI"],
        "secondary": ["optimisation de modèles", "compression", "benchmark"],
        "domain": ["machine learning", "deep learning", "cloud computing"]
    }
    concepts = {
        "verbs": ["réduire", "optimiser", "évaluer", "concevoir"],
        "nouns": ["énergie", "performance", "modèle", "apprentissage"]
    }
    
    test_titles = [
        "Machine Learning Approaches for Effective Energy-Efficient Resource Management",
        "AI-Enabled Autonomous Drones for Fast Climate Change Crisis Assessment",
        "Deep Learning Model Compression for Edge Devices"
    ]
    
    for title in test_titles:
        result = analyze_title(title, themes, concepts)
        print(f"\n📄 {title[:60]}...")
        print(f"   Decision: {result['decision']} (confidence: {result['confidence']})")
        print(f"   Reason: {result['reason']}")
