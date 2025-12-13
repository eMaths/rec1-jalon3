#!/usr/bin/env python3
"""
Script pour traiter tous les articles du fichier articles.csv selon les consignes de step1.md.
Génère result.csv et article_fetch_log.md dans le dossier results/.
"""

import csv
import json
import sys
import os
import time

# Ajouter le dossier tools au path pour importer fetch_article
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_article import fetch_article_metadata

# Problématique cible
PROBLEMATIQUE = """
Comment concevoir et évaluer des modèles d'apprentissage automatique plus durables 
en réduisant leur consommation d'énergie tout en conservant des performances satisfaisantes ?

Sujet: Green AI, efficacité énergétique des modèles d'apprentissage automatique (ML/AI).
"""

# Mots-clés pertinents pour le sujet
KEYWORDS_PERTINENTS = [
    "green ai", "green machine learning", "green deep learning",
    "energy efficient machine learning", "energy efficient deep learning", "energy efficient ai",
    "energy consumption machine learning", "energy consumption neural network",
    "sustainable ai", "sustainable machine learning",
    "carbon footprint ai", "carbon footprint machine learning",
    "model compression", "model pruning", "knowledge distillation",
    "efficient neural network", "efficient deep learning",
    "low power machine learning", "low power neural network",
    "energy aware training", "energy aware inference",
    "computational efficiency machine learning",
    "green computing ai", "environmentally sustainable ai",
]

# Mots-clés qui indiquent que l'article n'est PAS sur Green AI
KEYWORDS_NON_PERTINENTS = [
    "building energy", "smart building", "hvac", "heating ventilation",
    "vehicle energy", "electric vehicle", "fuel cell vehicle",
    "solar panel", "wind turbine", "renewable energy",
    "power grid", "smart grid", "energy grid",
    "battery management", "energy storage",
    "urban energy", "city energy",
    "wireless sensor network", "iot sensor",
    "medical device", "healthcare monitoring", "ecg", "electrocardiogram",
    "fault detection", "anomaly detection industrial",
    "drone", "uav", "unmanned aerial",
    "autonomous vehicle", "self driving",
    "climate change assessment", "environmental monitoring",
    "water management", "waste management",
    "agriculture", "soil", "crop",
    "landslide", "flood", "earthquake",
    "parkinson", "disease detection",
    "botnet", "security", "intrusion detection",
    "depth estimation", "image segmentation",
    "spectrum sensing", "lora network",
    "platoon", "traffic",
]


def is_title_relevant(title: str) -> tuple[bool, str]:
    """
    Analyse si le titre est pertinent pour la problématique Green AI.
    Retourne (is_relevant, reason)
    """
    title_lower = title.lower()
    
    # Vérifier les mots-clés non pertinents d'abord
    for kw in KEYWORDS_NON_PERTINENTS:
        if kw in title_lower:
            return False, f"Titre non pertinent - concerne '{kw}' et non l'efficacité énergétique des modèles ML"
    
    # Vérifier si le titre mentionne ML/AI + énergie/efficacité
    has_ml = any(term in title_lower for term in [
        "machine learning", "deep learning", "neural network", "ai ", "artificial intelligence",
        "reinforcement learning", "federated learning", "autoencoder", "transformer",
        "model", "algorithm", "benchmark"
    ])
    
    has_energy = any(term in title_lower for term in [
        "energy", "power", "efficient", "green", "sustainable", "carbon",
        "consumption", "optimization"
    ])
    
    # Si le titre parle de ML pour optimiser l'énergie de quelque chose d'autre (bâtiments, véhicules, etc.)
    # ce n'est PAS pertinent pour Green AI
    application_domains = [
        "building", "urban", "city", "vehicle", "truck", "bus", "car",
        "grid", "power plant", "solar", "wind", "geothermal",
        "manufacturing", "industrial", "factory", "semiconductor",
        "cloud", "data center", "server", "resource management",
        "wireless", "mobile", "iot", "sensor", "transmission",
        "healthcare", "medical", "clinical",
    ]
    
    for domain in application_domains:
        if domain in title_lower and has_ml:
            # C'est du ML appliqué à un domaine, pas du Green AI
            return False, f"Titre non pertinent - utilise ML pour optimiser '{domain}', pas pour réduire la consommation des modèles ML"
    
    # Cas spéciaux pertinents
    if "benchmark" in title_lower and "energy" in title_lower:
        return True, "Titre potentiellement pertinent - benchmarking énergétique"
    
    if "green" in title_lower and ("software" in title_lower or "computing" in title_lower):
        return True, "Titre potentiellement pertinent - green software/computing"
    
    # Si on n'a pas pu déterminer, on passe à l'abstract
    return True, "Titre à vérifier avec l'abstract"


def is_abstract_relevant(abstract: str, title: str) -> tuple[bool, str]:
    """
    Analyse si l'abstract confirme la pertinence pour Green AI.
    """
    if abstract == "Non disponible" or not abstract:
        return True, "Abstract non disponible - à vérifier manuellement"
    
    abstract_lower = abstract.lower()
    title_lower = title.lower()
    
    # Indicateurs forts de pertinence Green AI
    green_ai_indicators = [
        "energy consumption of model",
        "energy efficient model",
        "energy efficient neural",
        "energy efficient deep learning",
        "energy efficient machine learning",
        "reduce energy consumption",
        "reducing energy consumption",
        "energy footprint",
        "carbon footprint of model",
        "sustainable ai",
        "green ai",
        "model compression",
        "model pruning",
        "knowledge distillation",
        "efficient inference",
        "efficient training",
        "computational cost",
        "energy-aware",
        "power consumption of neural",
        "energy benchmark",
        "software energy",
    ]
    
    for indicator in green_ai_indicators:
        if indicator in abstract_lower:
            return True, "Prêt pour analyse de l'article"
    
    # Indicateurs que c'est du ML appliqué (pas Green AI)
    application_indicators = [
        "building energy consumption",
        "predict energy consumption",
        "forecast energy",
        "energy prediction",
        "energy forecasting",
        "hvac",
        "heating and cooling",
        "vehicle energy",
        "fuel consumption",
        "battery state",
        "power grid",
        "smart grid",
        "renewable energy",
        "solar energy",
        "wind energy",
        "ecg signal",
        "heart rhythm",
        "medical device",
        "healthcare",
        "fault detection",
        "anomaly detection",
        "climate change",
        "natural disaster",
        "flood",
        "drone",
        "uav",
        "wireless sensor",
        "iot device",
        "mobile phone",
        "transmission scheduling",
        "resource allocation",
        "cloud computing",
        "data center",
        "task scheduling",
    ]
    
    for indicator in application_indicators:
        if indicator in abstract_lower:
            return False, f"Abstract non pertinent - concerne l'application de ML pour '{indicator}'"
    
    # Si l'abstract parle d'efficacité énergétique mais dans un contexte applicatif
    if "energy" in abstract_lower:
        # Vérifier si c'est pour les modèles eux-mêmes ou pour une application
        if any(app in abstract_lower for app in ["building", "vehicle", "grid", "sensor", "device", "system"]):
            if not any(ml in abstract_lower for ml in ["model energy", "training energy", "inference energy"]):
                return False, "Abstract non pertinent - efficacité énergétique d'un système, pas des modèles ML"
    
    return True, "Prêt pour analyse de l'article"


def analyze_article(title: str, abstract: str) -> dict:
    """
    Analyse un article et retourne les raisons détaillées de la décision.
    """
    reasons = []
    is_relevant = True
    
    title_lower = title.lower()
    abstract_lower = abstract.lower() if abstract and abstract != "Non disponible" else ""
    
    # === Analyse du titre ===
    
    # Mots-clés qui indiquent clairement que ce n'est PAS Green AI
    non_green_ai_topics = {
        "building energy": "L'article traite de l'efficacité énergétique des bâtiments, pas des modèles ML",
        "smart building": "L'article traite des bâtiments intelligents, pas de l'efficacité des modèles ML",
        "urban energy": "L'article traite de l'énergie urbaine, pas des modèles ML",
        "vehicle energy": "L'article traite de l'énergie des véhicules, pas des modèles ML",
        "electric vehicle": "L'article traite des véhicules électriques, pas de l'efficacité des modèles ML",
        "fuel cell": "L'article traite des piles à combustible, pas des modèles ML",
        "solar panel": "L'article traite des panneaux solaires, pas des modèles ML",
        "wind turbine": "L'article traite des éoliennes, pas des modèles ML",
        "power grid": "L'article traite des réseaux électriques, pas des modèles ML",
        "smart grid": "L'article traite des réseaux intelligents, pas des modèles ML",
        "wireless sensor": "L'article traite des capteurs sans fil, pas de l'efficacité des modèles ML",
        "sensor network": "L'article traite des réseaux de capteurs, pas des modèles ML",
        "ecg": "L'article traite de signaux ECG médicaux, pas de l'efficacité des modèles ML",
        "electrocardiogram": "L'article traite de signaux ECG médicaux, pas de l'efficacité des modèles ML",
        "healthcare": "L'article traite de la santé, pas de l'efficacité des modèles ML",
        "medical device": "L'article traite de dispositifs médicaux, pas de l'efficacité des modèles ML",
        "parkinson": "L'article traite de la maladie de Parkinson, pas des modèles ML",
        "drone": "L'article traite des drones, pas de l'efficacité des modèles ML",
        "uav": "L'article traite des drones (UAV), pas de l'efficacité des modèles ML",
        "autonomous vehicle": "L'article traite des véhicules autonomes, pas de l'efficacité des modèles ML",
        "climate change": "L'article traite du changement climatique, pas des modèles ML",
        "flood": "L'article traite des inondations, pas des modèles ML",
        "landslide": "L'article traite des glissements de terrain, pas des modèles ML",
        "soil": "L'article traite du sol/agriculture, pas des modèles ML",
        "waste management": "L'article traite de la gestion des déchets, pas des modèles ML",
        "water management": "L'article traite de la gestion de l'eau, pas des modèles ML",
        "botnet": "L'article traite de la sécurité/botnets, pas de l'efficacité des modèles ML",
        "spectrum sensing": "L'article traite de la détection de spectre, pas des modèles ML",
        "platoon": "L'article traite des convois de véhicules, pas des modèles ML",
        "hvac": "L'article traite des systèmes HVAC, pas des modèles ML",
        "chiller": "L'article traite des refroidisseurs industriels, pas des modèles ML",
        "fault detection": "L'article traite de la détection de pannes, pas de l'efficacité des modèles ML",
        "depth estimation": "L'article traite de l'estimation de profondeur, pas de l'efficacité des modèles ML",
        "semiconductor manufacturing": "L'article traite de la fabrication de semi-conducteurs, pas des modèles ML",
        "data center": "L'article traite des centres de données, pas de l'efficacité des modèles ML eux-mêmes",
        "cloud computing": "L'article traite du cloud computing, pas de l'efficacité des modèles ML",
        "resource management": "L'article traite de la gestion des ressources, pas de l'efficacité des modèles ML",
        "task scheduling": "L'article traite de la planification de tâches, pas de l'efficacité des modèles ML",
        "mobile phone": "L'article traite des téléphones mobiles, pas de l'efficacité des modèles ML",
        "transmission scheduling": "L'article traite de la planification de transmissions, pas des modèles ML",
        "wireless powered": "L'article traite de l'alimentation sans fil, pas de l'efficacité des modèles ML",
        "mobile edge computing": "L'article traite du edge computing mobile, pas de l'efficacité des modèles ML",
        "iot": "L'article traite de l'IoT en général, pas de l'efficacité des modèles ML",
        "lora network": "L'article traite des réseaux LoRa, pas de l'efficacité des modèles ML",
    }
    
    # Mots-clés qui indiquent potentiellement Green AI
    green_ai_indicators = {
        "energy efficient model": "L'article mentionne l'efficacité énergétique des modèles",
        "energy efficient neural": "L'article traite de réseaux de neurones économes en énergie",
        "energy efficient deep learning": "L'article traite du deep learning économe en énergie",
        "energy efficient machine learning": "L'article traite du ML économe en énergie",
        "green ai": "L'article traite explicitement du Green AI",
        "sustainable ai": "L'article traite de l'IA durable",
        "model compression": "L'article traite de la compression de modèles",
        "model pruning": "L'article traite de l'élagage de modèles",
        "knowledge distillation": "L'article traite de la distillation de connaissances",
        "efficient inference": "L'article traite de l'inférence efficace",
        "efficient training": "L'article traite de l'entraînement efficace",
        "carbon footprint": "L'article traite de l'empreinte carbone des modèles",
        "energy consumption of model": "L'article traite de la consommation énergétique des modèles",
        "software energy": "L'article traite de l'énergie logicielle",
        "benchmark energy": "L'article traite du benchmarking énergétique",
        "green software": "L'article traite du logiciel vert",
        "energy aware training": "L'article traite de l'entraînement conscient de l'énergie",
        "computational efficiency": "L'article traite de l'efficacité computationnelle",
    }
    
    # Vérifier les indicateurs non-pertinents dans le titre
    for keyword, reason in non_green_ai_topics.items():
        if keyword in title_lower:
            reasons.append(f"❌ Titre: {reason}")
            is_relevant = False
            break
    
    # Si pas rejeté par le titre, vérifier les indicateurs positifs
    if is_relevant:
        found_positive = False
        for keyword, reason in green_ai_indicators.items():
            if keyword in title_lower:
                reasons.append(f"✅ Titre: {reason}")
                found_positive = True
                break
        
        if not found_positive:
            reasons.append("⚠️ Titre: Pas d'indicateur clair de Green AI, analyse de l'abstract nécessaire")
    
    # === Analyse de l'abstract ===
    if is_relevant and abstract_lower:
        # Vérifier les indicateurs non-pertinents dans l'abstract
        abstract_non_relevant = {
            "building energy consumption": "L'abstract traite de la consommation énergétique des bâtiments",
            "predict energy consumption": "L'abstract traite de la prédiction de consommation énergétique (pas des modèles ML)",
            "forecast energy": "L'abstract traite de la prévision énergétique",
            "hvac": "L'abstract traite des systèmes HVAC",
            "vehicle energy": "L'abstract traite de l'énergie des véhicules",
            "battery state": "L'abstract traite de l'état des batteries",
            "power grid": "L'abstract traite des réseaux électriques",
            "renewable energy": "L'abstract traite des énergies renouvelables",
            "ecg signal": "L'abstract traite de signaux ECG",
            "heart rhythm": "L'abstract traite de rythmes cardiaques",
            "natural disaster": "L'abstract traite de catastrophes naturelles",
            "wireless sensor": "L'abstract traite de capteurs sans fil",
            "iot device": "L'abstract traite de dispositifs IoT",
            "transmission scheduling": "L'abstract traite de planification de transmissions",
            "resource allocation": "L'abstract traite d'allocation de ressources",
            "task scheduling": "L'abstract traite de planification de tâches",
        }
        
        for keyword, reason in abstract_non_relevant.items():
            if keyword in abstract_lower:
                reasons.append(f"❌ Abstract: {reason}")
                is_relevant = False
                break
        
        # Vérifier les indicateurs positifs dans l'abstract
        if is_relevant:
            abstract_relevant_indicators = {
                "energy consumption of": "L'abstract mentionne la consommation énergétique",
                "reduce energy": "L'abstract parle de réduction d'énergie",
                "energy efficient": "L'abstract mentionne l'efficacité énergétique",
                "computational cost": "L'abstract traite du coût computationnel",
                "model compression": "L'abstract traite de compression de modèles",
                "pruning": "L'abstract mentionne l'élagage",
                "distillation": "L'abstract mentionne la distillation",
                "green": "L'abstract mentionne le terme 'green'",
                "sustainable": "L'abstract mentionne la durabilité",
            }
            
            found_abstract_positive = False
            for keyword, reason in abstract_relevant_indicators.items():
                if keyword in abstract_lower:
                    # Vérifier que c'est bien pour les modèles ML
                    ml_terms = ["model", "neural", "learning", "algorithm", "network", "training", "inference"]
                    if any(ml in abstract_lower for ml in ml_terms):
                        reasons.append(f"✅ Abstract: {reason} dans un contexte ML")
                        found_abstract_positive = True
                        break
            
            if not found_abstract_positive and is_relevant:
                reasons.append("⚠️ Abstract: Pas de confirmation claire de pertinence Green AI")
    
    elif is_relevant and (not abstract_lower or abstract == "Non disponible"):
        reasons.append("⚠️ Abstract non disponible - décision basée uniquement sur le titre")
    
    return {
        "is_relevant": is_relevant,
        "reasons": reasons
    }


def process_articles(input_csv: str, output_csv: str, log_md: str):
    """
    Traite tous les articles et génère les fichiers de sortie.
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
    log_entries = []
    
    for i, article in enumerate(articles):
        doi = article.get('doi', '').strip()
        if not doi:
            continue
            
        print(f"\n[{i+1}/{len(articles)}] Traitement de: {doi}")
        
        # Récupérer les métadonnées
        metadata = fetch_article_metadata(doi)
        
        if not metadata.get('success'):
            print(f"  ⚠ Erreur lors de la récupération: {metadata.get('error', 'Inconnu')}")
            # Utiliser les données du CSV original si disponibles
            metadata = {
                'doi': doi,
                'title': article.get('title', 'Non disponible'),
                'authors': article.get('author', 'Non disponible'),
                'abstract': 'Non disponible',
                'journal': article.get('journal', 'Non disponible'),
                'year': article.get('year', 'Non disponible'),
                'keywords': '',
                'success': False
            }
        
        title = metadata.get('title', 'Non disponible')
        authors = metadata.get('authors', 'Non disponible')
        abstract = metadata.get('abstract', 'Non disponible')
        journal = metadata.get('journal', 'Non disponible')
        year = metadata.get('year', 'Non disponible')
        keywords = metadata.get('keywords', '')
        
        print(f"  Titre: {title[:60]}...")
        
        # Analyser l'article avec justifications détaillées
        analysis = analyze_article(title, abstract)
        is_relevant = analysis["is_relevant"]
        reasons = analysis["reasons"]
        
        if is_relevant:
            selection = "pertinent"
            justification = "Prêt pour analyse de l'article"
            print(f"  ✅ Accepté")
        else:
            selection = "non pertinent"
            justification = reasons[0] if reasons else "Non pertinent"
            print(f"  ❌ Rejeté: {justification[:50]}...")
        
        # Ajouter au log avec le nouveau format
        log_entries.append({
            'title': title,
            'authors': authors,
            'doi': doi,
            'abstract': abstract,
            'is_relevant': is_relevant,
            'reasons': reasons
        })
        
        results.append({
            'Selection': selection,
            'title': title,
            'abstract': abstract[:500] + "..." if len(abstract) > 500 else abstract,
            'author': authors,
            'journal': journal,
            'Issue type': '',
            'year': year,
            'doi': doi,
            'keywords': keywords,
            'justification': justification
        })
        
        # Pause pour ne pas surcharger l'API
        time.sleep(0.5)
    
    # Écrire le CSV de résultats
    fieldnames = ['Selection', 'title', 'abstract', 'author', 'journal', 'Issue type', 'year', 'doi', 'keywords', 'justification']
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✅ Résultats écrits dans: {output_csv}")
    
    # Écrire le log markdown avec le nouveau format
    with open(log_md, 'w', encoding='utf-8') as f:
        f.write("# Log de récupération des articles\n\n")
        f.write(f"Date de traitement: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Nombre d'articles traités: {len(log_entries)}\n\n")
        f.write("**Problématique**: Comment concevoir et évaluer des modèles d'apprentissage automatique plus durables en réduisant leur consommation d'énergie tout en conservant des performances satisfaisantes ?\n\n")
        f.write("---\n\n")
        
        for entry in log_entries:
            f.write(f"## Article: {entry['title']}\n")
            f.write(f"- **Auteurs**: {entry['authors']}\n")
            f.write(f"- **Lien**: [DOI](https://doi.org/{entry['doi']})\n")
            f.write(f"- **Abstract**: {entry['abstract']}\n")
            f.write(f"- **Article retenu ?** {'True' if entry['is_relevant'] else 'False'}\n")
            f.write(f"- **Raisons**:\n")
            for reason in entry['reasons']:
                f.write(f"    - {reason}\n")
            f.write("\n---\n\n")
    
    print(f"✅ Log écrit dans: {log_md}")
    
    # Résumé
    pertinents = sum(1 for r in results if r['Selection'] == 'pertinent')
    non_pertinents = sum(1 for r in results if r['Selection'] == 'non pertinent')
    print(f"\n📊 Résumé:")
    print(f"   - Articles pertinents: {pertinents}")
    print(f"   - Articles non pertinents: {non_pertinents}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    input_csv = os.path.join(base_dir, "data", "articles.csv")
    output_csv = os.path.join(base_dir, "results", "result.csv")
    log_md = os.path.join(base_dir, "results", "article_fetch_log.md")
    
    process_articles(input_csv, output_csv, log_md)
