import sys
from pathlib import Path

# Garantit que la racine du projet est sur sys.path quelle que soit
# la façon dont Streamlit exécute ce fichier.
_project_root = str(Path(__file__).parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import streamlit as st

from frontend.utils.api import BACKEND_URL, fetch_machines, fetch_machines_list
from frontend.pages.machine_detail import render_machine_detail
from frontend.utils.ui import init_lang, load_machine_rows

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

machines = fetch_machines_list()

nav: dict[str, list] = {}
nav[""] = [
    st.Page("pages/dashboard.py", title="Dashboard", icon="🏠", url_path="dashboard"),
]
if machines:
    nav["Machines"] = [_make_machine_page(m["name"]) for m in machines]
nav["Gestion de production"] = [
    st.Page("pages/manufacturing_orders.py", title="Ordres de fabrication", icon="📋", url_path="manufacturing-orders"),
    st.Page("pages/downtimes.py", title="Arrêts", icon="⛔", url_path="downtimes"),
]

pg = st.navigation(nav)
pg.run()