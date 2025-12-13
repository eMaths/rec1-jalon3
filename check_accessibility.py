import csv
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


FILE_ENCODING = "utf-8"
ARXIV_PREFIXES = (
    "http://arxiv.org/",
    "https://arxiv.org/",
)

UNPAYWALL_EMAIL = "admin@example.com"


@dataclass
class Row:
    selection: str
    cols: list[str]


def _http_get_json(url: str, timeout_seconds: int = 20) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "rec1-jalon3-access-check/1.0",
            "Accept": "application/json",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
        return json.loads(raw)


def _looks_like_arxiv_url(s: str) -> bool:
    s = (s or "").strip()
    return any(s.startswith(p) for p in ARXIV_PREFIXES)


def _normalize_doi(doi: str) -> str:
    doi = (doi or "").strip()
    doi = re.sub(r"^https?://doi\.org/", "", doi, flags=re.IGNORECASE)
    doi = doi.strip()
    return doi


def _unpaywall_is_oa(doi: str, email: str) -> bool:
    doi = _normalize_doi(doi)
    if not doi:
        return False

    doi_enc = urllib.parse.quote(doi, safe="")
    email_enc = urllib.parse.quote(email, safe="")
    url = f"https://api.unpaywall.org/v2/{doi_enc}?email={email_enc}"

    try:
        data = _http_get_json(url)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return False

    if isinstance(data, dict):
        if data.get("is_oa") is True:
            return True

        best = data.get("best_oa_location")
        if isinstance(best, dict):
            if best.get("url") or best.get("url_for_pdf"):
                return True

        locations = data.get("oa_locations")
        if isinstance(locations, list):
            for loc in locations:
                if isinstance(loc, dict) and (loc.get("url") or loc.get("url_for_pdf")):
                    return True

    return False


def _semanticscholar_is_oa(doi: str, title: str) -> bool:
    # Legal OA discovery via Semantic Scholar Graph API.
    # We consider it accessible if it reports isOpenAccess=True or provides openAccessPdf.url.
    doi_norm = _normalize_doi(doi)
    urls: list[str] = []

    if doi_norm:
        doi_enc = urllib.parse.quote(doi_norm, safe="")
        urls.append(
            "https://api.semanticscholar.org/graph/v1/paper/DOI:"
            + doi_enc
            + "?fields=isOpenAccess,openAccessPdf,url"
        )

    title_q = (title or "").strip()
    if title_q:
        q_enc = urllib.parse.quote(title_q, safe="")
        urls.append(
            "https://api.semanticscholar.org/graph/v1/paper/search?query="
            + q_enc
            + "&limit=1&fields=isOpenAccess,openAccessPdf,url,title"
        )

    for url in urls:
        try:
            data = _http_get_json(url)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            continue

        # Direct endpoint returns a dict; search returns a dict with 'data' list.
        candidates: list[dict] = []
        if isinstance(data, dict) and isinstance(data.get("data"), list):
            candidates = [c for c in data.get("data") if isinstance(c, dict)]
        elif isinstance(data, dict):
            candidates = [data]

        for c in candidates:
            if c.get("isOpenAccess") is True:
                return True
            oapdf = c.get("openAccessPdf")
            if isinstance(oapdf, dict) and oapdf.get("url"):
                return True

    return False


def _openalex_is_oa(doi: str) -> bool:
    # Legal OA discovery via OpenAlex.
    doi_norm = _normalize_doi(doi)
    if not doi_norm:
        return False

    work_id = "https://doi.org/" + doi_norm
    work_enc = urllib.parse.quote(work_id, safe="")
    url = f"https://api.openalex.org/works/{work_enc}"

    try:
        data = _http_get_json(url)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return False

    if not isinstance(data, dict):
        return False

    oa = data.get("open_access")
    if isinstance(oa, dict):
        if oa.get("is_oa") is True:
            return True
        if oa.get("oa_url"):
            return True

    best = data.get("best_oa_location")
    if isinstance(best, dict) and (best.get("pdf_url") or best.get("landing_page_url")):
        return True

    locs = data.get("oa_locations")
    if isinstance(locs, list):
        for loc in locs:
            if isinstance(loc, dict) and (loc.get("pdf_url") or loc.get("landing_page_url")):
                return True

    return False


def _is_accessible(title: str, doi: str) -> bool:
    # Accessible if arXiv in DOI column OR a legal OA source confirms availability.
    if _looks_like_arxiv_url(doi):
        return True
    if _unpaywall_is_oa(doi, email=UNPAYWALL_EMAIL):
        return True
    if _openalex_is_oa(doi):
        return True
    if _semanticscholar_is_oa(doi, title=title):
        return True
    return False


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python tools/check_accessibility.py <path-to-selection_step1_table.txt>")
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        return 2

    with path.open("r", encoding=FILE_ENCODING, newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        rows = list(reader)

    if not rows:
        print("Empty file.")
        return 0

    header = rows[0]
    data_rows = rows[1:]

    updated = 0
    total_checked = 0

    out_rows = [header]
    for cols in data_rows:
        if not cols or all((c or "").strip() == "" for c in cols):
            out_rows.append(cols)
            continue

        selection = (cols[0] or "").strip()
        # Re-check both already-pertinent items and those previously marked non-accessible.
        if selection in ("Pertinent", "Très pertinent", "Non accessible"):
            total_checked += 1
            title = cols[1] if len(cols) > 1 else ""
            doi = cols[8] if len(cols) > 8 else ""

            accessible = _is_accessible(title=title, doi=doi)
            if accessible:
                if selection == "Non accessible":
                    cols = list(cols)
                    cols[0] = "Pertinent"
                    updated += 1
            else:
                if selection in ("Pertinent", "Très pertinent"):
                    cols = list(cols)
                    cols[0] = "Non accessible"
                    updated += 1

            # Be polite to Unpaywall
            time.sleep(0.25)

        out_rows.append(cols)

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding=FILE_ENCODING, newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerows(out_rows)

    tmp_path.replace(path)

    print(f"Checked={total_checked}")
    print(f"SelectionUpdated={updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
