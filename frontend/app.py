import sys
from pathlib import Path

# Garantit que la racine du projet est sur sys.path quelle que soit
# la façon dont Streamlit exécute ce fichier.
_project_root = str(Path(__file__).parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import streamlit as st

from frontend.utils.api import fetch_machines
from frontend.pages.machine_detail import render_machine_detail

st.set_page_config(
    page_title="Production",
    page_icon="🏭",
    layout="wide",
)


def _slugify(name: str) -> str:
    return name.lower().replace(" ", "-").replace("_", "-")


def _make_machine_page(machine_name: str):
    def _page():
        render_machine_detail(machine_name)

    _page.__name__ = f"machine_{machine_name.replace(' ', '_')}"
    return st.Page(
        _page,
        title=machine_name,
        url_path=f"machine-{_slugify(machine_name)}",
        icon="⚙️",
    )

def load_machine_rows():
    # --- Tableau des machines ---
    machines = fetch_machines()
    if machines is None:
        st.error(f"Impossible de joindre le backend sur {BACKEND_URL}. Vérifiez qu'il est démarré.")
        st.stop()

    st.session_state.rows = [
        {
            "Machine": m["machine_name"],
            "Pièces produites": m["pieces_produced"],
            "Pièces rejetées": m["pieces_rejected"],
            "Taux de rejet (%)": round(m["pieces_rejected"] / m["pieces_produced"] * 100, 1),
            "Temps d'utilisation (min)": m["usage_time_min"],
        }
        for m in machines
    ]

machines = fetch_machines()

nav: dict[str, list] = {}
nav[""] = [
    st.Page("pages/dashboard.py", title="Dashboard", icon="🏠", url_path="dashboard"),
]
if machines:
    nav["Machines"] = [_make_machine_page(m["machine_name"]) for m in machines]
nav["Gestion de production"] = [
    st.Page("pages/manufacturing_orders.py", title="Ordres de fabrication", icon="📋", url_path="manufacturing-orders"),
    st.Page("pages/downtimes.py", title="Arrêts", icon="⛔", url_path="downtimes"),
]

pg = st.navigation(nav)
pg.run()
