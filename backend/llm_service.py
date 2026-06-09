import json
import os

from google import genai
from google.genai import types

from backend.models import MachineData, ProductionIndicators

MODEL = "gemini-2.0-flash"
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        dotenv = dict(list(map(lambda line: line.split('='), open(".env", "r").readlines())))
        _client = genai.Client(api_key=dotenv["GEMINI_API_KEY"])
    return _client

_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "advices": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 5,
            "maxItems": 5,
        },
    },
    "required": ["summary", "advices"],
}


def generate_report_content(
    machines: list[MachineData],
    indicators: ProductionIndicators,
) -> dict:
    machines_detail = "\n".join(
        f"- {m.machine_name} : {m.pieces_produced} pièces produites, "
        f"{m.pieces_rejected} rejetées "
        f"(taux de rejet : {0 if m.pieces_produced == 0 else m.pieces_rejected / m.pieces_produced * 100:.1f}%), "
        f"temps d'utilisation : {m.usage_time_min} min"
        for m in machines
    )

    prompt = f"""Tu es un expert en production industrielle. Analyse les indicateurs de production suivants et génère un rapport en français.

Indicateurs globaux :
- Disponibilité : {indicators.availability * 100:.1f}%
- Performance : {indicators.performance * 100:.1f}%
- Qualité : {indicators.quality * 100:.1f}%
- TRS (OEE) : {indicators.trs * 100:.1f}%

Détail par machine :
{machines_detail}

Produis :
1. Une synthèse de 3 à 4 phrases décrivant l'état général de la production, les points forts et les points faibles observés.
2. Exactement 5 conseils concrets et actionnables d'amélioration ou de maintenance pour optimiser la production.
"""

    try:
        response = _get_client().models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=_RESPONSE_SCHEMA,
            ),
        )
        return json.loads(response.text)
    except Exception:
        return {
            "summary": "Erreur lors de la génération du rapport.",
            "advices": ["Vérifier la clé API GEMINI_API_KEY."] * 5,
        }
