#!/usr/bin/env python3
"""
Analyse de l'abstract d'un article par rapport aux thèmes extraits de analyse_problematique.md.

Règles (basées sur step4.md) :
- Si l'abstract confirme que l'article est hors sujet → rejeter
- Si l'abstract confirme une pertinence potentielle → accepter

Principes clés :
1. Distinguer "étudier le sujet" vs "utiliser le sujet comme outil"
2. Être inclusif : en cas de doute, préférer garder l'article
3. Ne rejeter que les articles CLAIREMENT hors domaine
"""

import re
from typing import Dict, List


def analyze_abstract(abstract: str, themes: Dict[str, List[str]], concepts: Dict[str, List[str]], 
                     title_analysis: Dict = None) -> Dict:
    """
    Analyse l'abstract d'un article par rapport aux thèmes extraits.
    
    Args:
        abstract: Le résumé de l'article
        themes: Dict avec clés "primary", "secondary", "domain" contenant les thèmes
        concepts: Dict avec clés "verbs", "nouns" contenant les concepts clés
        title_analysis: Résultat de l'analyse du titre (optionnel)
    
    Returns:
        {
            "decision": "accept" | "reject",
            "category": "A" | "B" | "C" | None,
            "confidence": float (0-1),
            "matched_themes": {"primary": [...], "secondary": [...], "domain": [...]},
            "matched_concepts": [...],
            "reason": str,
            "themes_identified": [...]
        }
    """
    # Cas spécial: abstract non disponible
    if not abstract or abstract == "Non disponible" or len(abstract) < 50:
        return {
            "decision": "accept",
            "category": "C",
            "confidence": 0.3,
            "matched_themes": {"primary": [], "secondary": [], "domain": []},
            "matched_concepts": [],
            "reason": "Abstract non disponible ou trop court, conservé par prudence",
            "themes_identified": ["Données insuffisantes"]
        }
    
    abstract_lower = abstract.lower()
    
    matched_themes = {
        "primary": [],
        "secondary": [],
        "domain": []
    }
    matched_concepts = []
    themes_identified = []
    
    # Chercher les correspondances avec les thèmes
    for category in ["primary", "secondary", "domain"]:
        for theme in themes.get(category, []):
            theme_lower = theme.lower()
            theme_words = [w for w in theme_lower.split() if len(w) > 3]
            
            # Match exact du thème
            if theme_lower in abstract_lower:
                matched_themes[category].append(theme)
                if theme not in themes_identified:
                    themes_identified.append(theme)
            # Match partiel (mots significatifs du thème)
            elif theme_words:
                matches = sum(1 for w in theme_words if w in abstract_lower)
                # Si plus de la moitié des mots sont présents
                if matches >= len(theme_words) / 2 and matches >= 1:
                    matched_themes[category].append(theme)
                    if theme not in themes_identified:
                        themes_identified.append(theme)
    
    # Chercher les correspondances avec les concepts
    all_concepts = concepts.get("verbs", []) + concepts.get("nouns", [])
    for concept in all_concepts:
        concept_lower = concept.lower()
        if len(concept_lower) > 3 and concept_lower in abstract_lower:
            matched_concepts.append(concept)
    
    # Calculer les scores
    primary_score = len(matched_themes["primary"])
    secondary_score = len(matched_themes["secondary"])
    domain_score = len(matched_themes["domain"])
    concept_score = len(matched_concepts)
    
    if not themes_identified:
        themes_identified = ["Aucun thème identifié"]
    
    # Logique de décision basée sur step4.md
    
    # Cas 1: Thèmes primaires trouvés → Catégorie A
    if primary_score >= 2:
        return {
            "decision": "accept",
            "category": "A",
            "confidence": 0.9,
            "matched_themes": matched_themes,
            "matched_concepts": matched_concepts,
            "reason": f"L'abstract correspond à {primary_score} thème(s) primaire(s): {matched_themes['primary']}",
            "themes_identified": themes_identified
        }
    
    if primary_score == 1:
        return {
            "decision": "accept",
            "category": "A",
            "confidence": 0.8,
            "matched_themes": matched_themes,
            "matched_concepts": matched_concepts,
            "reason": f"L'abstract correspond au thème primaire: {matched_themes['primary']}",
            "themes_identified": themes_identified
        }
    
    # Cas 2: Thèmes secondaires trouvés → Catégorie B
    if secondary_score >= 1:
        return {
            "decision": "accept",
            "category": "B",
            "confidence": 0.7,
            "matched_themes": matched_themes,
            "matched_concepts": matched_concepts,
            "reason": f"L'abstract correspond à {secondary_score} thème(s) secondaire(s): {matched_themes['secondary']}",
            "themes_identified": themes_identified
        }
    
    # Cas 3: Thèmes du domaine trouvés → Catégorie C
    if domain_score >= 1:
        return {
            "decision": "accept",
            "category": "C",
            "confidence": 0.5,
            "matched_themes": matched_themes,
            "matched_concepts": matched_concepts,
            "reason": f"L'abstract est dans le même domaine: {matched_themes['domain']}",
            "themes_identified": themes_identified
        }
    
    # Cas 4: Concepts clés trouvés mais pas de thèmes → Catégorie C avec prudence
    if concept_score >= 3:
        return {
            "decision": "accept",
            "category": "C",
            "confidence": 0.4,
            "matched_themes": matched_themes,
            "matched_concepts": matched_concepts,
            "reason": f"L'abstract contient {concept_score} concepts clés: {matched_concepts[:5]}",
            "themes_identified": themes_identified
        }
    
    # Cas 5: Aucune correspondance significative
    # Principe d'inclusivité : on garde quand même en C si le titre était prometteur
    if title_analysis and title_analysis.get("confidence", 0) >= 0.5:
        return {
            "decision": "accept",
            "category": "C",
            "confidence": 0.3,
            "matched_themes": matched_themes,
            "matched_concepts": matched_concepts,
            "reason": "Aucune correspondance dans l'abstract, mais le titre suggérait un lien possible",
            "themes_identified": themes_identified
        }
    
    # Cas 6: Vraiment aucun lien → Rejeter
    return {
        "decision": "reject",
        "category": None,
        "confidence": 0.6,
        "matched_themes": matched_themes,
        "matched_concepts": matched_concepts,
        "reason": "Aucune correspondance avec les thèmes ou concepts de la problématique",
        "themes_identified": themes_identified
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
    
    test_abstracts = [
        "This paper presents a methodology to reduce energy consumption in deep learning models while maintaining accuracy.",
        "We propose an AI-based pipeline for processing natural disaster images taken from drones.",
        "This article investigates machine learning techniques for cloud computing optimization."
    ]
    
    for abstract in test_abstracts:
        result = analyze_abstract(abstract, themes, concepts)
        print(f"\n📄 {abstract[:70]}...")
        print(f"   Decision: {result['decision']} | Category: {result['category']}")
        print(f"   Themes: {result['themes_identified']}")
        print(f"   Reason: {result['reason']}")
