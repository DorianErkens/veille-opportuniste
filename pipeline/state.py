"""État local : quelles offres ont déjà été traitées, par boîte.

Fichier séparé du tracker (cf. STORYMAP.md / PRD.md question ouverte #2) :
c'est un cache jetable pour le diff, pas la donnée de valeur.
"""
import json
from pathlib import Path


def load_state(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_state(path: Path, state: dict[str, list[str]]) -> None:
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def diff_new_postings(postings: list[dict], seen_ids: list[str]) -> list[dict]:
    seen = set(seen_ids)
    return [p for p in postings if p["id"] not in seen]
