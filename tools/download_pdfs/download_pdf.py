#!/usr/bin/env python3
"""
Outil pour télécharger les PDFs d'articles scientifiques.

Sources utilisées (dans l'ordre de priorité) :
1. Unpaywall - Accès ouvert légal
2. OpenAlex - Liens OA
3. Semantic Scholar - OpenAccess PDF
4. arXiv - Preprints
5. Europe PMC - Articles biomédicaux

Usage:
    python download_pdf.py <doi>
    python download_pdf.py --file dois.txt --output ./pdfs/
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

# Configuration
USER_AGENT = "ArticleDownloader/1.0 (mailto:research@example.com)"
UNPAYWALL_EMAIL = "research@example.com"
TIMEOUT_SECONDS = 30
RATE_LIMIT_DELAY = 0.5  # secondes entre les requêtes


@dataclass
class PDFSource:
    """Représente une source de PDF trouvée."""
    url: str
    source_name: str
    is_direct_pdf: bool = True


def _http_get_json(url: str) -> Optional[dict]:
    """Récupère du JSON depuis une URL."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def _download_file(url: str, output_path: Path) -> bool:
    """Télécharge un fichier depuis une URL."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/pdf,*/*",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            content = resp.read()
            
            # Vérifier que c'est bien un PDF
            if not content.startswith(b'%PDF'):
                return False
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(content)
            return True
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return False


def _normalize_doi(doi: str) -> str:
    """Normalise un DOI."""
    doi = (doi or "").strip()
    doi = re.sub(r"^https?://doi\.org/", "", doi, flags=re.IGNORECASE)
    return doi.strip()


def _doi_to_filename(doi: str) -> str:
    """Convertit un DOI en nom de fichier valide."""
    # Remplacer les caractères non valides
    filename = doi.replace("/", "_").replace(":", "_").replace("\\", "_")
    filename = re.sub(r'[<>"|?*]', "_", filename)
    return filename + ".pdf"


# ============================================================================
# Sources de téléchargement
# ============================================================================

def find_pdf_unpaywall(doi: str) -> Optional[PDFSource]:
    """Cherche un PDF via Unpaywall."""
    doi = _normalize_doi(doi)
    if not doi:
        return None
    
    doi_enc = urllib.parse.quote(doi, safe="")
    email_enc = urllib.parse.quote(UNPAYWALL_EMAIL, safe="")
    url = f"https://api.unpaywall.org/v2/{doi_enc}?email={email_enc}"
    
    data = _http_get_json(url)
    if not data:
        return None
    
    # Chercher le meilleur lien PDF
    best = data.get("best_oa_location")
    if isinstance(best, dict):
        pdf_url = best.get("url_for_pdf") or best.get("url")
        if pdf_url:
            return PDFSource(url=pdf_url, source_name="Unpaywall", is_direct_pdf=bool(best.get("url_for_pdf")))
    
    # Chercher dans les autres locations
    locations = data.get("oa_locations", [])
    for loc in locations:
        if isinstance(loc, dict):
            pdf_url = loc.get("url_for_pdf") or loc.get("url")
            if pdf_url:
                return PDFSource(url=pdf_url, source_name="Unpaywall", is_direct_pdf=bool(loc.get("url_for_pdf")))
    
    return None


def find_pdf_openalex(doi: str) -> Optional[PDFSource]:
    """Cherche un PDF via OpenAlex."""
    doi = _normalize_doi(doi)
    if not doi:
        return None
    
    work_id = "https://doi.org/" + doi
    work_enc = urllib.parse.quote(work_id, safe="")
    url = f"https://api.openalex.org/works/{work_enc}"
    
    data = _http_get_json(url)
    if not data:
        return None
    
    # Chercher dans open_access
    oa = data.get("open_access", {})
    if isinstance(oa, dict) and oa.get("oa_url"):
        return PDFSource(url=oa["oa_url"], source_name="OpenAlex", is_direct_pdf=False)
    
    # Chercher dans best_oa_location
    best = data.get("best_oa_location")
    if isinstance(best, dict):
        pdf_url = best.get("pdf_url") or best.get("landing_page_url")
        if pdf_url:
            return PDFSource(url=pdf_url, source_name="OpenAlex", is_direct_pdf=bool(best.get("pdf_url")))
    
    return None


def find_pdf_semantic_scholar(doi: str) -> Optional[PDFSource]:
    """Cherche un PDF via Semantic Scholar."""
    doi = _normalize_doi(doi)
    if not doi:
        return None
    
    doi_enc = urllib.parse.quote(doi, safe="")
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi_enc}?fields=isOpenAccess,openAccessPdf"
    
    data = _http_get_json(url)
    if not data:
        return None
    
    oapdf = data.get("openAccessPdf")
    if isinstance(oapdf, dict) and oapdf.get("url"):
        return PDFSource(url=oapdf["url"], source_name="SemanticScholar", is_direct_pdf=True)
    
    return None


def find_pdf_arxiv(doi: str) -> Optional[PDFSource]:
    """Cherche un PDF sur arXiv (si le DOI est un lien arXiv)."""
    doi = (doi or "").strip()
    
    # Vérifier si c'est un lien arXiv
    arxiv_match = re.search(r'arxiv\.org/abs/(\d+\.\d+)', doi, re.IGNORECASE)
    if arxiv_match:
        arxiv_id = arxiv_match.group(1)
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        return PDFSource(url=pdf_url, source_name="arXiv", is_direct_pdf=True)
    
    # Chercher via l'API arXiv si c'est un DOI normal
    # arXiv n'indexe pas par DOI, donc on skip
    return None


def find_pdf_europe_pmc(doi: str) -> Optional[PDFSource]:
    """Cherche un PDF via Europe PMC."""
    doi = _normalize_doi(doi)
    if not doi:
        return None
    
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:{doi}&format=json&resultType=core"
    
    data = _http_get_json(url)
    if not data:
        return None
    
    results = data.get("resultList", {}).get("result", [])
    if not results:
        return None
    
    article = results[0]
    
    # Chercher le lien PDF
    full_text_urls = article.get("fullTextUrlList", {}).get("fullTextUrl", [])
    for ft in full_text_urls:
        if isinstance(ft, dict):
            if ft.get("documentStyle") == "pdf":
                return PDFSource(url=ft["url"], source_name="EuropePMC", is_direct_pdf=True)
    
    # Fallback sur le lien PMC
    pmcid = article.get("pmcid")
    if pmcid:
        pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
        return PDFSource(url=pdf_url, source_name="PMC", is_direct_pdf=True)
    
    return None


# ============================================================================
# Fonction principale
# ============================================================================

def find_pdf_sources(doi: str) -> list[PDFSource]:
    """
    Cherche toutes les sources de PDF disponibles pour un DOI.
    Retourne une liste triée par priorité.
    """
    sources = []
    
    # Essayer chaque source
    finders = [
        ("Unpaywall", find_pdf_unpaywall),
        ("OpenAlex", find_pdf_openalex),
        ("SemanticScholar", find_pdf_semantic_scholar),
        ("arXiv", find_pdf_arxiv),
        ("EuropePMC", find_pdf_europe_pmc),
    ]
    
    for name, finder in finders:
        try:
            source = finder(doi)
            if source:
                sources.append(source)
        except Exception as e:
            print(f"  ⚠️ Erreur {name}: {e}", file=sys.stderr)
        time.sleep(RATE_LIMIT_DELAY)
    
    return sources


def download_pdf(doi: str, output_dir: Path) -> Tuple[bool, str, Optional[Path]]:
    """
    Télécharge le PDF d'un article.
    
    Returns:
        (success, message, output_path)
    """
    doi = _normalize_doi(doi)
    if not doi:
        return False, "DOI invalide", None
    
    # Chercher les sources
    sources = find_pdf_sources(doi)
    
    if not sources:
        return False, "Aucune source PDF trouvée", None
    
    # Essayer de télécharger depuis chaque source
    filename = _doi_to_filename(doi)
    output_path = output_dir / filename
    
    for source in sources:
        print(f"  📥 Tentative: {source.source_name} ({source.url[:60]}...)")
        
        if _download_file(source.url, output_path):
            return True, f"Téléchargé depuis {source.source_name}", output_path
    
    return False, f"Échec du téléchargement ({len(sources)} sources essayées)", None


def check_accessibility(doi: str) -> Tuple[bool, list[str]]:
    """
    Vérifie si un article est accessible en Open Access.
    
    Returns:
        (is_accessible, list_of_sources)
    """
    sources = find_pdf_sources(doi)
    source_names = [s.source_name for s in sources]
    return len(sources) > 0, source_names


# ============================================================================
# CLI
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Télécharge les PDFs d'articles scientifiques",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python download_pdf.py 10.1234/example.doi
  python download_pdf.py --check 10.1234/example.doi
  python download_pdf.py --file dois.txt --output ./pdfs/
        """
    )
    
    parser.add_argument(
        "doi",
        nargs="?",
        help="DOI de l'article à télécharger"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Vérifier l'accessibilité sans télécharger"
    )
    
    parser.add_argument(
        "--file", "-f",
        help="Fichier contenant une liste de DOIs (un par ligne)"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="./pdfs",
        help="Dossier de sortie pour les PDFs (défaut: ./pdfs)"
    )
    
    args = parser.parse_args()
    
    if not args.doi and not args.file:
        parser.print_help()
        return 1
    
    output_dir = Path(args.output)
    
    # Liste des DOIs à traiter
    dois = []
    if args.doi:
        dois.append(args.doi)
    if args.file:
        with open(args.file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    dois.append(line)
    
    print("=" * 60)
    print("📄 TÉLÉCHARGEMENT DE PDFs")
    print("=" * 60)
    print(f"📊 {len(dois)} article(s) à traiter")
    print(f"📁 Sortie: {output_dir.absolute()}")
    print("=" * 60)
    
    success_count = 0
    failed_dois = []
    
    for i, doi in enumerate(dois, 1):
        print(f"\n[{i}/{len(dois)}] {doi}")
        
        if args.check:
            accessible, sources = check_accessibility(doi)
            if accessible:
                print(f"  ✅ Accessible via: {', '.join(sources)}")
                success_count += 1
            else:
                print(f"  ❌ Non accessible")
                failed_dois.append(doi)
        else:
            success, message, path = download_pdf(doi, output_dir)
            if success:
                print(f"  ✅ {message}")
                print(f"     → {path}")
                success_count += 1
            else:
                print(f"  ❌ {message}")
                failed_dois.append(doi)
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    print(f"  ✅ Succès: {success_count}/{len(dois)}")
    print(f"  ❌ Échecs: {len(failed_dois)}/{len(dois)}")
    
    if failed_dois:
        print("\n📋 DOIs non accessibles:")
        for doi in failed_dois:
            print(f"  - {doi}")
    
    print("=" * 60)
    
    return 0 if not failed_dois else 1


if __name__ == "__main__":
    sys.exit(main())
