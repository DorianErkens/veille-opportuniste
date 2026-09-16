"""Tracker append-only : la donnée de valeur, ne jamais écraser."""
import json
from datetime import datetime, timezone
from pathlib import Path


def append_to_tracker(path: Path, entry: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def append_rejection_log(path: Path, entreprise: str, offre_id: str, rejetees: list[dict]) -> None:
    if not rejetees:
        return
    with path.open("a", encoding="utf-8") as f:
        for item in rejetees:
            f.write(json.dumps({
                "horodatage": datetime.now(timezone.utc).isoformat(),
                "entreprise": entreprise,
                "offre_id": offre_id,
                "terme": item.get("terme"),
                "citation_exacte": item.get("citation_exacte"),
            }, ensure_ascii=False) + "\n")


def read_tracker(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
