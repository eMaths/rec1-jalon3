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
from typing import Optional, Dict, List

# Pour le scraping HTML comme dernier recours
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


# Seuil minimum pour considérer un abstract comme "complet"
# Un abstract scientifique typique fait 150-300 mots (environ 1000-2000 caractères)
MIN_ABSTRACT_LENGTH = 200  # caractères minimum
MIN_ABSTRACT_WORDS = 30    # mots minimum


def is_valid_abstract(abstract: str) -> bool:
    """
    Vérifie si un abstract est valide (non vide, pas tronqué, assez long).
    Un abstract scientifique complet fait généralement 150-300 mots.
    """
    if not abstract or abstract == "Non disponible":
        return False
    
    # Vérifier la longueur minimale
    if len(abstract) < MIN_ABSTRACT_LENGTH:
        return False
    
    word_count = len(abstract.split())
    if word_count < MIN_ABSTRACT_WORDS:
        return False
    
    # Détecter les abstracts tronqués
    abstract_stripped = abstract.strip()
    
    # Finit par "..." ou "…"
    if abstract_stripped.endswith("...") or abstract_stripped.endswith("…"):
        return False
    
    # Finit par une phrase incomplète (pas de ponctuation finale)
    # Un abstract complet devrait finir par . ! ? ou )
    if not any(abstract_stripped.endswith(p) for p in ['.', '!', '?', ')', '"', "'"]):
        # Vérifier si c'est vraiment tronqué (moins de 500 caractères sans ponctuation finale)
        if len(abstract_stripped) < 500:
            return False
    
    return True


def clean_abstract(abstract: str) -> str:
    """
    Nettoie un abstract (supprime HTML, normalise les espaces).
    """
    if not abstract:
        return "Non disponible"
    
    # Supprimer les balises HTML
    abstract = re.sub(r'<[^>]+>', '', abstract)
    
    # Supprimer les entités HTML
    abstract = re.sub(r'&[a-zA-Z]+;', ' ', abstract)
    abstract = re.sub(r'&#\d+;', ' ', abstract)
    
    # Normaliser les espaces
    abstract = re.sub(r'\s+', ' ', abstract)
    abstract = abstract.strip()
    
    return abstract if abstract else "Non disponible"


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
    return clean_abstract(abstract)


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


def fetch_from_europe_pmc(doi: str) -> dict:
    """
    Récupère les métadonnées via Europe PMC API.
    Excellente source pour les abstracts scientifiques complets.
    """
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:{doi}&format=json&resultType=core"
    
    headers = {
        "User-Agent": "ArticleFetcher/1.0"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("resultList", {}).get("result", [])
        if not results:
            return None
        
        article = results[0]
        
        title = article.get("title", "Non disponible")
        
        # Extraire les auteurs
        author_list = article.get("authorList", {}).get("author", [])
        authors = [a.get("fullName", "") for a in author_list if a.get("fullName")]
        authors_str = ", ".join(authors) if authors else "Non disponible"
        
        # Abstract - Europe PMC a souvent des abstracts complets
        abstract = article.get("abstractText", "Non disponible")
        abstract = clean_abstract(abstract)
        
        journal = article.get("journalTitle", "Non disponible")
        year = article.get("pubYear", "Non disponible")
        
        # Mots-clés
        keywords_list = article.get("keywordList", {}).get("keyword", [])
        keywords_str = ", ".join(keywords_list[:5]) if keywords_list else "Non disponible"
        
        return {
            "doi": doi,
            "title": title,
            "authors": authors_str,
            "abstract": abstract,
            "journal": journal,
            "year": year,
            "keywords": keywords_str,
            "success": True,
            "source": "EuropePMC"
        }
        
    except requests.exceptions.RequestException as e:
        return None


def fetch_from_doi_scraping(doi: str) -> dict:
    """
    Dernier recours: scraper la page DOI.org pour récupérer l'abstract.
    Nécessite BeautifulSoup.
    """
    if not HAS_BS4:
        return None
    
    url = f"https://doi.org/{doi}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        candidates = []
        
        # Stratégie 1: meta tag DC.description ou citation_abstract
        for meta_name in ['DC.description', 'citation_abstract', 'description', 'og:description']:
            meta = soup.find('meta', {'name': meta_name}) or soup.find('meta', {'property': meta_name})
            if meta and meta.get('content'):
                content = clean_abstract(meta['content'])
                if len(content) > 50:
                    candidates.append(content)
        
        # Stratégie 2: section/div avec class contenant "abstract"
        for elem in soup.find_all(['div', 'section', 'article', 'p'], class_=lambda x: x and 'abstract' in str(x).lower() if x else False):
            text = elem.get_text(separator=' ', strip=True)
            text = clean_abstract(text)
            # Supprimer le mot "Abstract" au début s'il est présent
            if text.lower().startswith('abstract'):
                text = text[8:].strip()
                if text.startswith(':'):
                    text = text[1:].strip()
            if len(text) > 100:
                candidates.append(text)
        
        # Stratégie 3: élément avec id contenant "abstract"
        for elem in soup.find_all(id=lambda x: x and 'abstract' in x.lower() if x else False):
            text = elem.get_text(separator=' ', strip=True)
            text = clean_abstract(text)
            if text.lower().startswith('abstract'):
                text = text[8:].strip()
                if text.startswith(':'):
                    text = text[1:].strip()
            if len(text) > 100:
                candidates.append(text)
        
        # Stratégie 4: heading "Abstract" suivi de paragraphes
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
            heading_text = heading.get_text().strip().lower()
            if heading_text == 'abstract' or heading_text.startswith('abstract'):
                # Récupérer tous les paragraphes suivants jusqu'au prochain heading
                paragraphs = []
                for sibling in heading.find_next_siblings():
                    if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                        break
                    if sibling.name in ['p', 'div']:
                        paragraphs.append(sibling.get_text(separator=' ', strip=True))
                if paragraphs:
                    text = clean_abstract(' '.join(paragraphs))
                    if len(text) > 100:
                        candidates.append(text)
        
        # Stratégie 5: data-abstract attribute
        for elem in soup.find_all(attrs={'data-abstract': True}):
            text = clean_abstract(elem.get('data-abstract', ''))
            if len(text) > 100:
                candidates.append(text)
        
        # Choisir le meilleur candidat (le plus long qui est valide, sinon le plus long)
        if candidates:
            # Trier par longueur décroissante
            candidates.sort(key=len, reverse=True)
            
            # Chercher d'abord un candidat valide
            for candidate in candidates:
                if is_valid_abstract(candidate):
                    return {
                        "doi": doi,
                        "title": "Non disponible",
                        "authors": "Non disponible",
                        "abstract": candidate,
                        "journal": "Non disponible",
                        "year": "Non disponible",
                        "keywords": "Non disponible",
                        "success": True,
                        "source": "DOI_Scraping"
                    }
            
            # Sinon, retourner le plus long même s'il n'est pas "valide"
            best = candidates[0]
            if len(best) > 100:
                return {
                    "doi": doi,
                    "title": "Non disponible",
                    "authors": "Non disponible",
                    "abstract": best,
                    "journal": "Non disponible",
                    "year": "Non disponible",
                    "keywords": "Non disponible",
                    "success": True,
                    "source": "DOI_Scraping"
                }
        
        return None
        
    except Exception as e:
        return None


def merge_results(base: dict, supplement: dict, source_name: str) -> dict:
    """
    Fusionne deux résultats, en prenant les meilleures valeurs de chaque.
    Priorité à l'abstract le plus long et le plus complet.
    """
    if not base:
        return supplement
    if not supplement:
        return base
    
    result = base.copy()
    
    # Fusionner l'abstract - prendre le plus long/complet
    base_abstract = base.get("abstract", "Non disponible")
    supp_abstract = supplement.get("abstract", "Non disponible")
    
    if not is_valid_abstract(base_abstract) and is_valid_abstract(supp_abstract):
        result["abstract"] = supp_abstract
        result["source"] = f"{base.get('source', 'Unknown')}+{source_name}"
    elif is_valid_abstract(base_abstract) and is_valid_abstract(supp_abstract):
        # Prendre le plus long
        if len(supp_abstract) > len(base_abstract):
            result["abstract"] = supp_abstract
            result["source"] = f"{base.get('source', 'Unknown')}+{source_name}"
    
    # Compléter les autres champs manquants
    for field in ["title", "authors", "journal", "year", "keywords"]:
        if result.get(field) in [None, "Non disponible", "Erreur", ""]:
            supp_value = supplement.get(field)
            if supp_value and supp_value not in [None, "Non disponible", "Erreur", ""]:
                result[field] = supp_value
    
    return result


def fetch_article_metadata(doi: str) -> dict:
    """
    Récupère les métadonnées d'un article en essayant plusieurs sources.
    Stratégie améliorée: essaie TOUTES les sources et fusionne les résultats
    pour maximiser les chances d'obtenir un abstract complet.
    
    Ordre de priorité:
    1. OpenAlex (index inversé, souvent complet)
    2. Europe PMC (excellente source pour abstracts scientifiques)
    3. Semantic Scholar (bonne couverture)
    4. CrossRef (métadonnées officielles)
    5. Unpaywall (métadonnées de base)
    6. DOI Scraping (dernier recours)
    
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
    
    sources_tried = []
    result = None
    
    # Source 1: OpenAlex (meilleur pour les abstracts via index inversé)
    openalex_result = fetch_from_openalex(doi)
    sources_tried.append("OpenAlex")
    if openalex_result:
        result = openalex_result
    
    # Source 2: Europe PMC (excellente source pour abstracts complets)
    if not is_valid_abstract(result.get("abstract") if result else None):
        epmc_result = fetch_from_europe_pmc(doi)
        sources_tried.append("EuropePMC")
        if epmc_result:
            result = merge_results(result, epmc_result, "EuropePMC")
    
    # Source 3: Semantic Scholar
    if not is_valid_abstract(result.get("abstract") if result else None):
        ss_result = fetch_from_semantic_scholar(doi)
        sources_tried.append("SemanticScholar")
        if ss_result:
            result = merge_results(result, ss_result, "SemanticScholar")
    
    # Source 4: CrossRef (métadonnées officielles, parfois abstracts)
    if not is_valid_abstract(result.get("abstract") if result else None):
        crossref_result = fetch_from_crossref(doi)
        sources_tried.append("CrossRef")
        if crossref_result:
            result = merge_results(result, crossref_result, "CrossRef")
    
    # Source 5: Unpaywall (métadonnées de base, rarement abstracts)
    if result is None:
        unpaywall_result = fetch_from_unpaywall(doi)
        sources_tried.append("Unpaywall")
        if unpaywall_result:
            result = unpaywall_result
    
    # Source 6: DOI Scraping (dernier recours)
    if not is_valid_abstract(result.get("abstract") if result else None):
        scraping_result = fetch_from_doi_scraping(doi)
        sources_tried.append("DOI_Scraping")
        if scraping_result:
            result = merge_results(result, scraping_result, "DOI_Scraping")
    
    # Si aucun résultat
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
    
    # Marquer si l'abstract est valide ou non
    result["abstract_valid"] = is_valid_abstract(result.get("abstract", ""))
    result["abstract_length"] = len(result.get("abstract", ""))
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
