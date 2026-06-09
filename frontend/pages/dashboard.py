import requests

import plotly.graph_objects as go
import streamlit as st

from frontend.utils.api import fetch_machines
from frontend.pages.machine_detail import render_machine_detail

from url import BACKEND_URL
from frontend.i18n import i18n
from frontend.utils.ui import init_lang, load_machine_rows

init_lang()

st.set_page_config(page_title=i18n("page_title"), layout="wide")
st.title(i18n("page_title"))

st.set_page_config(
    page_title="Production",
    page_icon="🏭",
    layout="wide",
)

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

st.title(i18n("dashboard"))

machines = fetch_machines()
machine_names = [m["machine_name"] for m in machines]

load_machine_rows()
st.subheader(i18n("machines_data"))
st.dataframe(st.session_state.rows, use_container_width=True)

tab_labels = ["Global"] + machine_names
tabs = st.tabs(tab_labels)

# --- Onglet Global ---
with tabs[0]:
    if not machines:
        st.error("Impossible de joindre le backend sur http://localhost:8000. Vérifiez qu'il est démarré.")
    else:
        # --- Bouton de génération ---
        if st.button(i18n("generate_report"), type="primary"):
            with st.spinner(i18n("ongoing_report_generation")):
                try:
                    response = requests.post(f"{BACKEND_URL}/report/generate", timeout=60)
                    response.raise_for_status()
                    st.session_state.report = response.json()
                except requests.exceptions.ConnectionError:
                    st.error(i18n("backend_connection_error"))
                except Exception as e:
                    st.error(f"{i18n('report_generation_error')} : {e}")

        # --- Affichage du rapport ---
        if st.session_state.get("report"):
            report = st.session_state.report
            ind = report["global_indicators"]

            st.subheader(i18n("global_indicators"))
            c1, c2, c3, c4 = st.columns(4)
            c1.plotly_chart(_make_gauge(i18n("gauge_availability"), ind["availability"]), use_container_width=True)
            c2.plotly_chart(_make_gauge(i18n("gauge_performance"), ind["performance"]), use_container_width=True)
            c3.plotly_chart(_make_gauge(i18n("gauge_quality"), ind["quality"]), use_container_width=True)
            c4.plotly_chart(_make_gauge(i18n("gauge_trs"), ind["trs"]), use_container_width=True)

            st.subheader(i18n("synthesis"))
            st.info(report["summary_text"])

            st.subheader(i18n("recommendations"))
            for i, advice in enumerate(report["advices"], 1):
                st.markdown(f"**{i}.** {advice}")

# --- Onglets par machine ---
for i, machine_name in enumerate(machine_names):
    with tabs[i + 1]:
        render_machine_detail(machine_name)
