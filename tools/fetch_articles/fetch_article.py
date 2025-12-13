#!/usr/bin/env python3
"""
Outil pour récupérer les métadonnées d'articles scientifiques via OpenAlex API.
Retourne titre, auteurs et abstract à partir d'un DOI.
OpenAlex est une base de données ouverte qui contient les abstracts.
"""

import requests
import json
import sys
import re
from urllib.parse import quote


def reconstruct_abstract(inverted_index: dict) -> str:
    """
    Reconstruit l'abstract à partir de l'index inversé d'OpenAlex.
    L'index inversé mappe chaque mot à ses positions dans le texte.
    """
    if not inverted_index:
        return "Non disponible"
    
    # Créer une liste de tuples (position, mot)
    words_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            words_positions.append((pos, word))
    
    # Trier par position
    words_positions.sort(key=lambda x: x[0])
    
    # Reconstruire le texte
    abstract = " ".join([word for _, word in words_positions])
    return abstract


def fetch_from_openalex(doi: str) -> dict:
    """
    Récupère les métadonnées via OpenAlex API.
    """
    url = f"https://api.openalex.org/works/doi:{doi}"
    
    headers = {
        "User-Agent": "ArticleFetcher/1.0 (mailto:research@example.com)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extraire le titre
        title = data.get("title", "Non disponible")
        
        # Extraire les auteurs
        authorships = data.get("authorships", [])
        authors = []
        for authorship in authorships:
            author_info = authorship.get("author", {})
            name = author_info.get("display_name", "")
            if name:
                authors.append(name)
        authors_str = ", ".join(authors) if authors else "Non disponible"
        
        # Extraire l'abstract (index inversé)
        abstract_inverted = data.get("abstract_inverted_index", {})
        abstract = reconstruct_abstract(abstract_inverted)
        
        # Extraire le journal
        primary_location = data.get("primary_location", {}) or {}
        source = primary_location.get("source", {}) or {}
        journal = source.get("display_name", "Non disponible")
        if journal == "Non disponible":
            # Fallback sur le nom brut
            locations = data.get("locations", [])
            if locations:
                journal = locations[0].get("raw_source_name", "Non disponible")
        
        # Extraire l'année
        year = data.get("publication_year", "Non disponible")
        
        # Extraire les mots-clés
        keywords_list = data.get("keywords", [])
        keywords = [kw.get("display_name", "") for kw in keywords_list if kw.get("display_name")]
        keywords_str = ", ".join(keywords[:5]) if keywords else "Non disponible"  # Limiter à 5
        
        return {
            "doi": doi,
            "title": title,
            "authors": authors_str,
            "abstract": abstract,
            "journal": journal,
            "year": year,
            "keywords": keywords_str,
            "success": True,
            "source": "OpenAlex"
        }
        
    except requests.exceptions.RequestException as e:
        return None


def fetch_from_semantic_scholar(doi: str) -> dict:
    """
    Récupère les métadonnées via Semantic Scholar API.
    """
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,authors,abstract,year,venue"
    
    headers = {
        "User-Agent": "ArticleFetcher/1.0"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        title = data.get("title", "Non disponible")
        
        authors_list = data.get("authors", [])
        authors = [a.get("name", "") for a in authors_list if a.get("name")]
        authors_str = ", ".join(authors) if authors else "Non disponible"
        
        abstract = data.get("abstract") or "Non disponible"
        journal = data.get("venue") or "Non disponible"
        year = data.get("year") or "Non disponible"
        
        return {
            "doi": doi,
            "title": title,
            "authors": authors_str,
            "abstract": abstract,
            "journal": journal,
            "year": year,
            "keywords": "Non disponible",
            "success": True,
            "source": "SemanticScholar"
        }
        
    except requests.exceptions.RequestException as e:
        return None


def fetch_from_unpaywall(doi: str) -> dict:
    """
    Récupère les métadonnées via Unpaywall API (accès ouvert).
    """
    url = f"https://api.unpaywall.org/v2/{doi}?email=research@example.com"
    
    headers = {
        "User-Agent": "ArticleFetcher/1.0"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        title = data.get("title", "Non disponible")
        
        authors_list = data.get("z_authors", [])
        authors = []
        for a in authors_list:
            name = f"{a.get('given', '')} {a.get('family', '')}".strip()
            if name:
                authors.append(name)
        authors_str = ", ".join(authors) if authors else "Non disponible"
        
        # Unpaywall n'a pas d'abstract directement
        abstract = "Non disponible"
        journal = data.get("journal_name") or "Non disponible"
        year = data.get("year") or "Non disponible"
        
        return {
            "doi": doi,
            "title": title,
            "authors": authors_str,
            "abstract": abstract,
            "journal": journal,
            "year": year,
            "keywords": "Non disponible",
            "success": True,
            "source": "Unpaywall"
        }
        
    except requests.exceptions.RequestException as e:
        return None


def fetch_from_crossref(doi: str) -> dict:
    """
    Récupère les métadonnées via CrossRef API (fallback).
    """
    encoded_doi = quote(doi, safe='')
    url = f"https://api.crossref.org/works/{encoded_doi}"
    
    headers = {
        "User-Agent": "ArticleFetcher/1.0 (mailto:research@example.com)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        message = data.get("message", {})
        
        # Extraire le titre
        title_list = message.get("title", [])
        title = title_list[0] if title_list else "Non disponible"
        
        # Extraire les auteurs
        authors_list = message.get("author", [])
        authors = []
        for author in authors_list:
            given = author.get("given", "")
            family = author.get("family", "")
            if given and family:
                authors.append(f"{given} {family}")
            elif family:
                authors.append(family)
        authors_str = ", ".join(authors) if authors else "Non disponible"
        
        # Extraire l'abstract
        abstract = message.get("abstract", "Non disponible")
        if abstract != "Non disponible":
            abstract = re.sub(r'<[^>]+>', '', abstract)
            abstract = abstract.strip()
        
        # Extraire le journal
        container = message.get("container-title", [])
        journal = container[0] if container else "Non disponible"
        
        # Extraire l'année
        published = message.get("published", {})
        date_parts = published.get("date-parts", [[]])
        year = date_parts[0][0] if date_parts and date_parts[0] else "Non disponible"
        
        # Extraire les mots-clés
        keywords = message.get("subject", [])
        keywords_str = ", ".join(keywords) if keywords else "Non disponible"
        
        return {
            "doi": doi,
            "title": title,
            "authors": authors_str,
            "abstract": abstract,
            "journal": journal,
            "year": year,
            "keywords": keywords_str,
            "success": True,
            "source": "CrossRef"
        }
        
    except requests.exceptions.RequestException as e:
        return None


def fetch_article_metadata(doi: str) -> dict:
    """
    Récupère les métadonnées d'un article en essayant plusieurs sources.
    Ordre: OpenAlex -> Semantic Scholar -> CrossRef -> Unpaywall
    
    Args:
        doi: Le DOI de l'article (ex: "10.1145/3598301" ou "https://doi.org/10.1145/3598301")
    
    Returns:
        dict avec title, authors, abstract, journal, year, keywords
    """
    # Nettoyer le DOI
    if doi.startswith("https://doi.org/"):
        doi = doi.replace("https://doi.org/", "")
    elif doi.startswith("http://doi.org/"):
        doi = doi.replace("http://doi.org/", "")
    
    # Essayer OpenAlex d'abord (meilleur pour les abstracts)
    result = fetch_from_openalex(doi)
    sources_tried = ["OpenAlex"]
    
    # Si OpenAlex n'a pas d'abstract, essayer Semantic Scholar
    if result is None or result.get("abstract") == "Non disponible":
        ss_result = fetch_from_semantic_scholar(doi)
        sources_tried.append("SemanticScholar")
        if ss_result and ss_result.get("abstract") != "Non disponible":
            if result:
                result["abstract"] = ss_result["abstract"]
                result["source"] = "OpenAlex+SemanticScholar"
            else:
                result = ss_result
    
    # Si toujours pas d'abstract, essayer CrossRef
    if result is None or result.get("abstract") == "Non disponible":
        crossref_result = fetch_from_crossref(doi)
        sources_tried.append("CrossRef")
        if crossref_result:
            if result and crossref_result.get("abstract") != "Non disponible":
                result["abstract"] = crossref_result["abstract"]
                result["source"] = f"{result.get('source', 'Unknown')}+CrossRef"
            elif crossref_result and result is None:
                result = crossref_result
    
    # Dernière tentative avec Unpaywall pour les métadonnées de base
    if result is None:
        result = fetch_from_unpaywall(doi)
        sources_tried.append("Unpaywall")
    
    if result is None:
        return {
            "doi": doi,
            "title": "Erreur",
            "authors": "Erreur",
            "abstract": "Erreur - Impossible de récupérer depuis: " + ", ".join(sources_tried),
            "journal": "Erreur",
            "year": "Erreur",
            "keywords": "Erreur",
            "success": False,
            "error": "Impossible de récupérer les métadonnées depuis: " + ", ".join(sources_tried)
        }
    
    result["sources_tried"] = sources_tried
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_article.py <DOI>")
        print("Exemple: python fetch_article.py 10.1145/3598301")
        sys.exit(1)
    
    doi = sys.argv[1]
    result = fetch_article_metadata(doi)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
