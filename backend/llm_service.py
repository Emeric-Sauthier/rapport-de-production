import json
import logging
import os
import time

from google import genai
from google.genai import errors, types

from backend.models import MachineData, ProductionIndicators

logger = logging.getLogger(__name__)

# Modele principal (surchargeable via .env), puis modeles de repli essayes dans
# l'ordre si le quota journalier du precedent est epuise.
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
_DEFAULT_FALLBACKS = "gemini-2.5-flash,gemini-2.5-flash-lite"
_FALLBACK_MODELS = os.environ.get("GEMINI_FALLBACK_MODELS", _DEFAULT_FALLBACKS)

# Tentatives et delai de base (s) pour absorber un rate limit par minute.
_MAX_ATTEMPTS = 3
_RETRY_BASE_DELAY_S = 4

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY absente : renseigne-la dans un fichier .env a la racine "
                "du projet (copie .env.example en .env) puis relance le backend."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def _model_chain() -> list[str]:
    """Modele configure en tete, suivi des replis, sans doublon."""
    chain: list[str] = []
    for name in [MODEL, *_FALLBACK_MODELS.split(",")]:
        name = name.strip()
        if name and name not in chain:
            chain.append(name)
    return chain


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


def _build_prompt(
    machines: list[MachineData],
    indicators: ProductionIndicators,
) -> str:
    machines_detail = "\n".join(
        f"- {m.machine_name} : {m.pieces_produced} pièces produites, "
        f"{m.pieces_rejected} rejetées "
        f"(taux de rejet : {0 if m.pieces_produced == 0 else m.pieces_rejected / m.pieces_produced * 100:.1f}%), "
        f"temps d'utilisation : {m.usage_time_min} min"
        for m in machines
    )
    return f"""Tu es un expert en production industrielle. Analyse les indicateurs de production suivants et génère un rapport en français.

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


class _ModelExhausted(Exception):
    """Le modele a epuise son quota (ou rate limit persistant) : il faut basculer."""


def _generate_with_model(
    model: str,
    prompt: str,
    config: types.GenerateContentConfig,
) -> dict:
    """Appelle un modele, avec retry sur rate limit par minute.

    Leve _ModelExhausted si le quota journalier est epuise ou si le rate limit
    persiste apres les tentatives : l'appelant basculera vers le modele suivant.
    """
    for attempt in range(_MAX_ATTEMPTS):
        try:
            response = _get_client().models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            return json.loads(response.text)
        except errors.ClientError as e:
            msg = str(e)
            if not (getattr(e, "code", None) == 429 or "RESOURCE_EXHAUSTED" in msg):
                raise  # autre erreur 4xx : ne pas masquer, ne pas basculer
            # Quota journalier epuise : inutile de retenter ce modele, on bascule.
            if "PerDay" in msg:
                raise _ModelExhausted(model)
            # Rate limit par minute : on patiente puis on retente le meme modele.
            if attempt < _MAX_ATTEMPTS - 1:
                delay = _RETRY_BASE_DELAY_S * (attempt + 1)
                logger.warning(
                    "Rate limit Gemini sur '%s' (429), nouvel essai dans %ss (%s/%s)",
                    model, delay, attempt + 1, _MAX_ATTEMPTS,
                )
                time.sleep(delay)
                continue
            raise _ModelExhausted(model)
    raise _ModelExhausted(model)


def generate_report_content(
    machines: list[MachineData],
    indicators: ProductionIndicators,
) -> dict:
    prompt = _build_prompt(machines, indicators)
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=_RESPONSE_SCHEMA,
        # Thinking inutile pour un rapport de formatage : on le coupe pour
        # accelerer la reponse et reduire la consommation de tokens.
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )

    chain = _model_chain()
    for model in chain:
        try:
            result = _generate_with_model(model, prompt, config)
            if model != chain[0]:
                logger.info("Rapport genere via le modele de repli '%s'", model)
            return result
        except _ModelExhausted:
            logger.warning("Modele '%s' sature, bascule vers le suivant", model)
            continue
        except Exception:
            logger.exception("Echec de la generation du rapport via Gemini")
            break

    logger.error("Aucun modele disponible (satures ou en echec) : %s", ", ".join(chain))
    return {
        "summary": "Erreur lors de la génération du rapport.",
        "advices": ["Vérifier la clé API GEMINI_API_KEY et la connexion réseau."] * 5,
    }
