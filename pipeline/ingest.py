"""Ingestion depuis les APIs publiques des ATS. v0 : Lever uniquement."""
import json
import urllib.request


def fetch_lever_postings(company_slug: str) -> list[dict]:
    """Récupère les offres publiées d'une boîte sur Lever, format normalisé."""
    url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
    with urllib.request.urlopen(url, timeout=15) as resp:
        raw = json.load(resp)

    return [
        {
            "id": posting["id"],
            "entreprise": company_slug,
            "titre": posting["text"],
            "url": posting["hostedUrl"],
            "date_publication": posting["createdAt"],
            "texte_offre": _flatten_lever_description(posting),
        }
        for posting in raw
    ]


def _flatten_lever_description(posting: dict) -> str:
    parts = [posting.get("descriptionPlain", "")]
    for section in posting.get("listsPlain", []) or posting.get("lists", []):
        parts.append(section.get("text", ""))
        parts.extend(section.get("content", "").split("\n") if section.get("content") else [])
    return "\n".join(p for p in parts if p)
