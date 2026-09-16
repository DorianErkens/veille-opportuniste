"""Digest v0 : affichage brut du tracker, pas d'agrégation (cf. STORYMAP.md)."""
from pathlib import Path

from pipeline.store import read_tracker


def print_raw_digest(tracker_path: Path) -> None:
    entries = read_tracker(tracker_path)
    if not entries:
        print("Tracker vide — aucune offre traitée pour l'instant.")
        return

    for entry in entries:
        outils = ", ".join(o["terme"] for o in entry["outils_valides"]) or "(aucun outil validé)"
        print(f"- [{entry['entreprise']}] {entry['poste']} ({entry['date']}) → {outils}")
        print(f"  {entry['lien']}")
