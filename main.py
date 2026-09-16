"""Walking skeleton (STORYMAP.md v0) : 1 source (Lever/Scaleway), 1 extracteur,
extract-then-verify, tracker append-only, digest brut.

Usage :
    python main.py                       # run réel (Lever + Ollama si dispo)
    python main.py --extractor stub      # démo hors-ligne, sans réseau ni Ollama
"""
import argparse
from pathlib import Path

from pipeline.digest import print_raw_digest
from pipeline.extract import OllamaExtractor, StubExtractor
from pipeline.ingest import fetch_lever_postings
from pipeline.state import diff_new_postings, load_state, save_state
from pipeline.store import append_rejection_log, append_to_tracker

DATA_DIR = Path("data")
STATE_PATH = DATA_DIR / "state.json"
TRACKER_PATH = DATA_DIR / "tracker.jsonl"
REJECTS_PATH = DATA_DIR / "rejects.jsonl"

COMPANY = "scaleway"  # walking skeleton : 1 seule boîte


def run(extractor) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    state = load_state(STATE_PATH)
    seen_ids = state.get(COMPANY, [])

    postings = fetch_lever_postings(COMPANY)
    nouvelles = diff_new_postings(postings, seen_ids)
    print(f"{len(postings)} offres au total, {len(nouvelles)} nouvelles.")

    for posting in nouvelles:
        extractions = extractor.extract(posting["texte_offre"])
        from pipeline.verify import verify_extractions
        validees, rejetees = verify_extractions(extractions, posting["texte_offre"])

        append_to_tracker(TRACKER_PATH, {
            "entreprise": posting["entreprise"],
            "poste": posting["titre"],
            "date": posting["date_publication"],
            "lien": posting["url"],
            "outils_valides": validees,
        })
        append_rejection_log(REJECTS_PATH, posting["entreprise"], posting["id"], rejetees)

        print(f"  {posting['titre']}: {len(validees)} validé(s), {len(rejetees)} rejeté(s)")

    state[COMPANY] = seen_ids + [p["id"] for p in nouvelles]
    save_state(STATE_PATH, state)

    print("\n--- Digest ---")
    print_raw_digest(TRACKER_PATH)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extractor", choices=["ollama", "stub"], default="ollama")
    parser.add_argument("--model", default="llama3.2")
    args = parser.parse_args()

    if args.extractor == "stub":
        chosen = StubExtractor()
    else:
        chosen = OllamaExtractor(model=args.model)

    run(chosen)
