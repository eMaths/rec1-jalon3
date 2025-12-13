#!/usr/bin/env python3
"""
Analyse du titre d'un article par rapport aux keywords extraits de keywords.json.

Règles (basées sur step4.md) :
- Si le titre contient des keywords → passer à l'abstract
- On ne rejette JAMAIS sur le titre seul (principe d'inclusivité)
"""

from typing import Dict, List


def analyze_title(title: str, keywords: Dict) -> Dict:
    """
    Analyse le titre d'un article par rapport aux keywords.
    
    Args:
        title: Le titre de l'article
        keywords: Dict avec clés "primary", "secondary", "domain", "all_keywords"
    
    Returns:
        {
            "decision": "continue" (toujours, on ne rejette pas sur le titre),
            "confidence": float (0-1),
            "matched_by_category": {"primary": [...], "secondary": [...], "domain": [...]},
            "matched_keywords": [...],
            "reason": str
        }
    """
    title_lower = title.lower()
    
    matched_by_category = {
        "primary": [],
        "secondary": [],
        "domain": []
    }
    matched_keywords = []
    
    # Chercher les correspondances par catégorie
    for category in ["primary", "secondary", "domain"]:
        for keyword in keywords.get(category, []):
            keyword_lower = keyword.lower().strip()
            if len(keyword_lower) > 2 and keyword_lower in title_lower:
                matched_by_category[category].append(keyword)
                if keyword_lower not in matched_keywords:
                    matched_keywords.append(keyword_lower)
    
    # Calculer les scores
    primary_score = len(matched_by_category["primary"])
    secondary_score = len(matched_by_category["secondary"])
    domain_score = len(matched_by_category["domain"])
    
    # Logique de décision - on ne rejette JAMAIS sur le titre seul
    
    if primary_score >= 1:
        return {
            "decision": "continue",
            "confidence": 0.9,
            "matched_by_category": matched_by_category,
            "matched_keywords": matched_keywords,
            "reason": f"Titre contient {primary_score} keyword(s) primaire(s): {matched_by_category['primary']}"
        }
    
    if secondary_score >= 1:
        return {
            "decision": "continue",
            "confidence": 0.7,
            "matched_by_category": matched_by_category,
            "matched_keywords": matched_keywords,
            "reason": f"Titre contient {secondary_score} keyword(s) secondaire(s): {matched_by_category['secondary']}"
        }
    
    if domain_score >= 1:
        return {
            "decision": "continue",
            "confidence": 0.5,
            "matched_by_category": matched_by_category,
            "matched_keywords": matched_keywords,
            "reason": f"Titre contient {domain_score} keyword(s) du domaine: {matched_by_category['domain']}"
        }
    
    # Aucune correspondance → continuer quand même (être inclusif)
    return {
        "decision": "continue",
        "confidence": 0.3,
        "matched_by_category": matched_by_category,
        "matched_keywords": matched_keywords,
        "reason": "Aucune correspondance dans le titre, vérification de l'abstract nécessaire"
    }


if __name__ == "__main__":
    # Test avec des keywords simulés
    keywords = {
        "primary": ["energy efficiency", "energy-efficient", "energy consumption", "green AI"],
        "secondary": ["model compression", "pruning", "quantization"],
        "domain": ["machine learning", "deep learning", "cloud computing"],
        "all_keywords": []
    }
    
    test_titles = [
        "Machine Learning Approaches for Effective Energy-Efficient Resource Management",
        "AI-Enabled Autonomous Drones for Fast Climate Change Crisis Assessment",
        "Deep Learning Model Compression for Edge Devices"
    ]
    
    for title in test_titles:
        result = analyze_title(title, keywords)
        print(f"\n📄 {title[:60]}...")
        print(f"   Decision: {result['decision']} (confidence: {result['confidence']})")
        print(f"   Matched: {result['matched_keywords']}")
        print(f"   Reason: {result['reason']}")
