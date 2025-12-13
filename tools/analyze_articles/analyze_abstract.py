#!/usr/bin/env python3
"""
Analyse de l'abstract d'un article par rapport aux keywords extraits de keywords.json.

Règles (basées sur step4.md) :
- Si l'abstract contient des keywords primaires → Catégorie A
- Si l'abstract contient des keywords secondaires → Catégorie B
- Si l'abstract contient des keywords du domaine → Catégorie C
- Sinon → rejeter

Principes clés :
1. Être inclusif : en cas de doute, préférer garder l'article
2. Ne rejeter que les articles CLAIREMENT hors domaine
"""

from typing import Dict, List


def analyze_abstract(abstract: str, keywords: Dict, title_analysis: Dict = None) -> Dict:
    """
    Analyse l'abstract d'un article par rapport aux keywords.
    
    Args:
        abstract: Le résumé de l'article
        keywords: Dict avec clés "primary", "secondary", "domain", "all_keywords"
        title_analysis: Résultat de l'analyse du titre (optionnel)
    
    Returns:
        {
            "decision": "accept" | "reject",
            "category": "A" | "B" | "C" | None,
            "confidence": float (0-1),
            "matched_by_category": {"primary": [...], "secondary": [...], "domain": [...]},
            "matched_keywords": [...],
            "reason": str
        }
    """
    # Cas spécial: abstract non disponible
    if not abstract or abstract == "Non disponible" or len(abstract) < 50:
        # Si le titre avait des correspondances, on garde l'article
        if title_analysis and title_analysis.get("matched_keywords"):
            return {
                "decision": "accept",
                "category": "C",
                "confidence": 0.4,
                "matched_by_category": title_analysis.get("matched_by_category", {}),
                "matched_keywords": title_analysis.get("matched_keywords", []),
                "reason": "Abstract non disponible, mais le titre contient des keywords pertinents"
            }
        return {
            "decision": "accept",
            "category": "C",
            "confidence": 0.3,
            "matched_by_category": {"primary": [], "secondary": [], "domain": []},
            "matched_keywords": [],
            "reason": "Abstract non disponible ou trop court, conservé par prudence"
        }
    
    abstract_lower = abstract.lower()
    
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
            if len(keyword_lower) > 2 and keyword_lower in abstract_lower:
                matched_by_category[category].append(keyword)
                if keyword_lower not in matched_keywords:
                    matched_keywords.append(keyword_lower)
    
    # Ajouter les correspondances du titre si disponibles
    if title_analysis:
        for kw in title_analysis.get("matched_keywords", []):
            if kw not in matched_keywords:
                matched_keywords.append(kw)
    
    # Calculer les scores
    primary_score = len(matched_by_category["primary"])
    secondary_score = len(matched_by_category["secondary"])
    domain_score = len(matched_by_category["domain"])
    
    # Logique de décision basée sur step4.md
    
    # Cas 1: Keywords primaires trouvés → Catégorie A
    if primary_score >= 1:
        return {
            "decision": "accept",
            "category": "A",
            "confidence": 0.9 if primary_score >= 2 else 0.8,
            "matched_by_category": matched_by_category,
            "matched_keywords": matched_keywords,
            "reason": f"Abstract contient {primary_score} keyword(s) primaire(s): {matched_by_category['primary']}"
        }
    
    # Cas 2: Keywords secondaires trouvés → Catégorie B
    if secondary_score >= 1:
        return {
            "decision": "accept",
            "category": "B",
            "confidence": 0.7,
            "matched_by_category": matched_by_category,
            "matched_keywords": matched_keywords,
            "reason": f"Abstract contient {secondary_score} keyword(s) secondaire(s): {matched_by_category['secondary']}"
        }
    
    # Cas 3: Keywords du domaine trouvés → Catégorie C
    if domain_score >= 1:
        return {
            "decision": "accept",
            "category": "C",
            "confidence": 0.5,
            "matched_by_category": matched_by_category,
            "matched_keywords": matched_keywords,
            "reason": f"Abstract contient {domain_score} keyword(s) du domaine: {matched_by_category['domain']}"
        }
    
    # Cas 4: Aucune correspondance dans l'abstract mais le titre était prometteur
    if title_analysis and title_analysis.get("confidence", 0) >= 0.5:
        return {
            "decision": "accept",
            "category": "C",
            "confidence": 0.4,
            "matched_by_category": matched_by_category,
            "matched_keywords": matched_keywords,
            "reason": "Aucune correspondance dans l'abstract, mais le titre contient des keywords pertinents"
        }
    
    # Cas 5: Vraiment aucun lien → Rejeter
    return {
        "decision": "reject",
        "category": None,
        "confidence": 0.6,
        "matched_by_category": matched_by_category,
        "matched_keywords": matched_keywords,
        "reason": "Aucune correspondance avec les keywords de la problématique"
    }


if __name__ == "__main__":
    # Test avec des keywords simulés
    keywords = {
        "primary": ["energy efficiency", "energy-efficient", "energy consumption", "green AI"],
        "secondary": ["model compression", "pruning", "quantization"],
        "domain": ["machine learning", "deep learning", "cloud computing"],
        "all_keywords": []
    }
    
    test_abstracts = [
        "This paper presents a methodology to reduce energy consumption in deep learning models while maintaining accuracy.",
        "We propose an AI-based pipeline for processing natural disaster images taken from drones.",
        "This article investigates machine learning techniques for cloud computing optimization."
    ]
    
    for abstract in test_abstracts:
        result = analyze_abstract(abstract, keywords)
        print(f"\n📄 {abstract[:70]}...")
        print(f"   Decision: {result['decision']} | Category: {result['category']}")
        print(f"   Matched: {result['matched_keywords']}")
        print(f"   Reason: {result['reason']}")
