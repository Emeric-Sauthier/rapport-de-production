"""Diagnostic de la connexion au LLM Gemini.

Lance un appel reel minimal et affiche un diagnostic clair sur ce qui marche
ou ce qui bloque.

Usage (depuis la racine rapport-de-production/) :
    python -m scripts.check_llm
    # ou
    python scripts/check_llm.py
"""
import logging
import os
import sys
from pathlib import Path

# Permet l'import de `backend` quel que soit le repertoire de lancement.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

import backend  # noqa: E402,F401  (l'import charge le .env)
from backend.main import compute_global_indicators  # noqa: E402
from backend.mock_data import get_mock_machines  # noqa: E402
from backend.llm_service import MODEL, generate_report_content  # noqa: E402


def main() -> int:
    print("=== Diagnostic connexion LLM (Gemini) ===")

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("[X] GEMINI_API_KEY absente.")
        print("    Copie .env.example en .env a la racine, renseigne ta cle, puis relance.")
        print("    Obtenir une cle : https://aistudio.google.com/apikey")
        return 1
    print(f"[OK] Cle presente (longueur {len(key)}). Modele cible : {MODEL}")

    machines = get_mock_machines()
    indicators = compute_global_indicators(machines)

    print("[..] Appel Gemini en cours (peut prendre quelques secondes)...")
    result = generate_report_content(machines, indicators)

    summary = result.get("summary", "")
    advices = result.get("advices", [])
    if summary.startswith("Erreur lors de la"):
        print("[X] Appel echoue. Le stacktrace est logge ci-dessus (niveau ERROR).")
        print("    Causes frequentes : cle invalide, quota depasse, pas de reseau.")
        return 2

    print("[OK] Reponse recue de Gemini.")
    print(f"     Synthese : {summary[:140]}{'...' if len(summary) > 140 else ''}")
    print(f"     Conseils : {len(advices)} generes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
