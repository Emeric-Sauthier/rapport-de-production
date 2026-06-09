# POC — Rapport de Production Industrielle

Application de démonstration composée d'un backend FastAPI et d'un frontend Streamlit pour visualiser les indicateurs TRS (OEE) d'une ligne de production.

## Prérequis

- Python 3.11+
- Une clé API Google Gemini

> **Important** : toutes les commandes ci-dessous doivent être exécutées depuis le répertoire racine `rapport-de-production/`, pas depuis un sous-dossier.

## Étape 1 — Installation des dépendances

Depuis `rapport-de-production/` :

```powershell
pip install -r requirements.txt
```

## Étape 2 — Configuration de la clé API

### Windows (PowerShell) — dans chaque terminal utilisé
Créez un fichier `.env` à la racine et mettez-y votre clef API comme ci-dessous :  
```
GEMINI_API_KEY=<votre_clé_api>
```

## Étape 3 — Démarrer le backend (terminal 1)

Depuis `rapport-de-production/` :

```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

> Si `uvicorn` est dans votre PATH, vous pouvez aussi utiliser :
> ```powershell
> uvicorn backend.main:app --reload --port 8000
> ```

L'API est accessible sur http://localhost:8000  
Documentation interactive : http://localhost:8000/docs

## Étape 4 — Démarrer le frontend (terminal 2)

Depuis `rapport-de-production/` :

```powershell
python -m streamlit run frontend/app.py
```

L'interface s'ouvre automatiquement sur http://localhost:8501

## Endpoints disponibles

| Méthode | Endpoint              | Description                              |
|---------|-----------------------|------------------------------------------|
| GET     | `/machines`           | Liste des machines avec leurs données    |
| GET     | `/indicators/global`  | Indicateurs TRS agrégés                  |
| POST    | `/report/generate`    | Génère un rapport complet via Gemini LLM |

## Structure du projet

```
rapport-de-production/
├── backend/
│   ├── __init__.py
│   ├── main.py          # Application FastAPI
│   ├── models.py        # Modèles Pydantic v2
│   ├── mock_data.py     # Données simulées (2 machines)
│   └── llm_service.py   # Intégration Gemini 2.0 Flash
├── frontend/
│   └── app.py           # Interface Streamlit
├── requirements.txt
└── README.md
```

## Calcul OEE (TRS)

- **Disponibilité** = Temps d'utilisation / Temps planifié
- **Performance** = Pièces produites / (Cadence théorique × Temps d'utilisation)
- **Qualité** = (Pièces produites − Pièces rejetées) / Pièces produites
- **TRS** = Disponibilité × Performance × Qualité
