"""Extraction ouverte des outils/frameworks mentionnés, via SLM.

Interface volontairement pluggable : le choix du modèle sort du protocole
d'éval (PRD.md section 3), pas d'un choix arbitraire figé dans le code.
"""
import json
import urllib.request
from typing import Protocol

PROMPT_TEMPLATE = """Tu analyses une offre d'emploi tech. Identifie chaque outil, \
framework, langage ou technologie explicitement mentionné dans le texte.

Pour chaque outil trouvé, cite la phrase EXACTE du texte source qui le mentionne \
(copie mot pour mot, ne reformule pas).

Réponds uniquement en JSON, une liste d'objets {{"terme": ..., "citation_exacte": ...}}.
Si aucun outil n'est mentionné, réponds [].

Texte de l'offre :
---
{texte}
---
"""


class Extractor(Protocol):
    def extract(self, texte_offre: str) -> list[dict]:
        ...


class OllamaExtractor:
    """Extracteur réel : appelle un modèle local via l'API Ollama (localhost:11434)."""

    def __init__(self, model: str, host: str = "http://localhost:11434"):
        self.model = model
        self.host = host

    def extract(self, texte_offre: str) -> list[dict]:
        payload = json.dumps({
            "model": self.model,
            "prompt": PROMPT_TEMPLATE.format(texte=texte_offre),
            "format": "json",
            "stream": False,
        }).encode()
        req = urllib.request.Request(
            f"{self.host}/api/generate", data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.load(resp)
        try:
            return json.loads(body["response"])
        except (json.JSONDecodeError, KeyError):
            return []


class StubExtractor:
    """Extracteur factice pour dev/démo hors-ligne, sans dépendance à Ollama.

    Simule volontairement une extraction imparfaite (une citation légèrement
    reformulée) pour exercer le rejet à l'étape de vérification.
    """

    def __init__(self, fake_outputs: dict[str, list[dict]] | None = None):
        self.fake_outputs = fake_outputs or {}

    def extract(self, texte_offre: str) -> list[dict]:
        return self.fake_outputs.get(texte_offre, [])
