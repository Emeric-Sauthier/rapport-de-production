"""Diagnostic de l'intermittence de /report/generate.

Appelle l'API Gemini N fois avec exactement la meme requete que le backend,
et detaille chaque reponse pour identifier la cause des echecs (~1 sur 2).

Usage (racine du projet, venv 3.13) :
    .\.venv\Scripts\python.exe scripts\diag_generation.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import backend  # noqa: E402,F401  (charge le .env)
from google.genai import types  # noqa: E402
from backend.mock_data import get_mock_machines  # noqa: E402
from backend.main import compute_global_indicators  # noqa: E402
from backend.llm_service import MODEL, _RESPONSE_SCHEMA, _get_client  # noqa: E402

machines = get_mock_machines()
ind = compute_global_indicators(machines)
machines_detail = "\n".join(
    f"- {m.machine_name} : {m.pieces_produced} pieces produites, "
    f"{m.pieces_rejected} rejetees, temps d'utilisation : {m.usage_time_min} min"
    for m in machines
)
prompt = f"""Tu es un expert en production industrielle. Analyse les indicateurs suivants et genere un rapport en francais.

Indicateurs globaux :
- Disponibilite : {ind.availability * 100:.1f}%
- Performance : {ind.performance * 100:.1f}%
- Qualite : {ind.quality * 100:.1f}%
- TRS (OEE) : {ind.trs * 100:.1f}%

Detail par machine :
{machines_detail}

Produis :
1. Une synthese de 3 a 4 phrases.
2. Exactement 5 conseils concrets d'amelioration ou de maintenance.
"""

client = _get_client()
N = 8
ok = 0
print(f"Modele : {MODEL} | {N} appels\n")
for i in range(N):
    tag = f"[{i + 1}/{N}] "
    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=_RESPONSE_SCHEMA,
            ),
        )
        cand = (resp.candidates or [None])[0]
        fr = getattr(cand, "finish_reason", None)
        um = resp.usage_metadata
        thoughts = getattr(um, "thoughts_token_count", None)
        out_tok = getattr(um, "candidates_token_count", None)
        try:
            txt = resp.text
        except Exception as e:
            txt = None
            tag += f"[text a leve: {type(e).__name__}] "
        tlen = len(txt) if txt else 0
        jok, nadv, jerr = False, None, None
        if txt:
            try:
                d = json.loads(txt)
                jok = True
                nadv = len(d.get("advices", []))
            except Exception as e:
                jerr = type(e).__name__
        if jok:
            ok += 1
        status = "OK   " if jok else "ECHEC"
        print(
            f"{tag}{status} finish={fr} thoughts_tok={thoughts} out_tok={out_tok} "
            f"text_len={tlen} json_ok={jok} advices={nadv}"
            + (f" json_err={jerr}" if jerr else "")
        )
    except Exception as e:
        print(f"{tag}EXCEPTION {type(e).__name__}: {str(e)[:130]}")
    time.sleep(4)

print(f"\n=> {ok}/{N} succes ({100 * ok // N}%)")
