import requests

import plotly.graph_objects as go
import streamlit as st

from frontend.utils.api import fetch_machines
from frontend.pages.machine_detail import render_machine_detail

BACKEND_URL = "http://localhost:8000"


def _make_gauge(title: str, value: float) -> go.Figure:
    pct = min(value * 100, 100)
    color = "green" if pct >= 80 else ("orange" if pct >= 60 else "red")
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=pct,
            number={"suffix": "%", "font": {"size": 28}},
            title={"text": title, "font": {"size": 16}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 60], "color": "#ffcccc"},
                    {"range": [60, 80], "color": "#ffe5cc"},
                    {"range": [80, 100], "color": "#ccffcc"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 2},
                    "thickness": 0.75,
                    "value": pct,
                },
            },
        )
    )
    fig.update_layout(height=250, margin={"t": 40, "b": 0, "l": 20, "r": 20})
    return fig


st.title("Dashboard")

machines = fetch_machines()
machine_names = [m["machine_name"] for m in machines]

tab_labels = ["Global"] + machine_names
tabs = st.tabs(tab_labels)

# --- Onglet Global ---
with tabs[0]:
    if not machines:
        st.error("Impossible de joindre le backend sur http://localhost:8000. Vérifiez qu'il est démarré.")
    else:
        rows = [
            {
                "Machine": m["machine_name"],
                "Cible": m["pieces_target"],
                "Pièces produites": m["pieces_produced"],
                "Pièces rejetées": m["pieces_rejected"],
                "Taux de rejet (%)": round(m["pieces_rejected"] / m["pieces_produced"] * 100, 1) if m["pieces_produced"] > 0 else 0.0,
                "Temps d'utilisation (min)": m["usage_time_min"],
                "Temps planifié (min)": m["planned_time_min"],
            }
            for m in machines
        ]
        st.subheader("Données machines")
        st.dataframe(rows, use_container_width=True)

        if st.button("Générer le rapport", type="primary"):
            with st.spinner("Génération du rapport en cours..."):
                try:
                    resp = requests.post(f"{BACKEND_URL}/report/generate", timeout=60)
                    resp.raise_for_status()
                    st.session_state.report = resp.json()
                except requests.exceptions.ConnectionError:
                    st.error("Impossible de joindre le backend. Vérifiez qu'il est démarré sur le port 8000.")
                except Exception as e:
                    st.error(f"Erreur lors de la génération du rapport : {e}")

        if st.session_state.get("report"):
            report = st.session_state.report
            ind = report["global_indicators"]

            st.subheader("Indicateurs globaux")
            c1, c2, c3, c4 = st.columns(4)
            c1.plotly_chart(_make_gauge("Disponibilité", ind["availability"]), use_container_width=True)
            c2.plotly_chart(_make_gauge("Performance", ind["performance"]), use_container_width=True)
            c3.plotly_chart(_make_gauge("Qualité", ind["quality"]), use_container_width=True)
            c4.plotly_chart(_make_gauge("TRS (OEE)", ind["trs"]), use_container_width=True)

            st.subheader("Synthèse")
            st.info(report["summary_text"])

            st.subheader("Recommandations")
            for i, advice in enumerate(report["advices"], 1):
                st.markdown(f"**{i}.** {advice}")

# --- Onglets par machine ---
for i, machine_name in enumerate(machine_names):
    with tabs[i + 1]:
        render_machine_detail(machine_name)
