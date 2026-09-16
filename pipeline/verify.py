"""Vérification déterministe (extract-then-verify) : aucun jugement LLM ici.

Une extraction est valide seulement si sa citation existe verbatim
(normalisée) dans le texte source. Sinon : rejet + log.
"""
import re


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def verify_extractions(extractions: list[dict], texte_offre: str) -> tuple[list[dict], list[dict]]:
    """Retourne (validées, rejetées)."""
    haystack = _normalize(texte_offre)
    validees, rejetees = [], []

    for item in extractions:
        citation = item.get("citation_exacte", "")
        if citation and _normalize(citation) in haystack:
            validees.append(item)
        else:
            rejetees.append(item)

    return validees, rejetees
