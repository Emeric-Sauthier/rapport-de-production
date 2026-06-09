"""Package backend.

Charge les variables d'environnement depuis un fichier .env a la racine du
projet des l'import, afin de ne plus avoir a redefinir GEMINI_API_KEY dans
chaque terminal.
"""
from pathlib import Path

from dotenv import load_dotenv

_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)
