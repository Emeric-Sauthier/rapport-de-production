import requests
import streamlit as st
import plotly.graph_objects as go

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Rapport de Production", layout="wide")
st.title("Rapport de Production Industrielle")

if "report" not in st.session_state:
    st.session_state.report = None


def fetch_machines():
    try:
        resp = requests.get(f"{BACKEND_URL}/machines", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def make_gauge(title: str, value: float) -> go.Figure:
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

def load_machine_rows():
    # --- Tableau des machines ---
    machines = fetch_machines()
    if machines is None:
        st.error("Impossible de joindre le backend sur http://localhost:8000. Vérifiez qu'il est démarré.")
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

load_machine_rows()
st.subheader("Données machines")
st.dataframe(st.session_state.rows, use_container_width=True)

uploaded_file = st.file_uploader(
    "Choisir un fichier CSV",
    type=["csv"],
    label_visibility="hidden"
)

# --- Bouton de génération ---
if st.button("Générer le rapport", type="primary"):
    with st.spinner("Génération du rapport en cours..."):
        try:
            if uploaded_file:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "text/csv"
                    )
                }

                response = requests.post(
                    "http://localhost:8000/import-csv",
                    files=files
                )
                load_machine_rows()
                st.rerun()
            else:
                response = requests.post(f"{BACKEND_URL}/report/generate", timeout=60)
            response.raise_for_status()
            st.session_state.report = response.json()
        except requests.exceptions.ConnectionError:
            st.error("Impossible de joindre le backend. Vérifiez qu'il est démarré sur le port 8000.")
        except Exception as e:
            st.error(f"Erreur lors de la génération du rapport : {e}")

# --- Affichage du rapport ---
if st.session_state.report:
    report = st.session_state.report
    ind = report["global_indicators"]

    st.subheader("Indicateurs globaux")
    c1, c2, c3, c4 = st.columns(4)
    c1.plotly_chart(make_gauge("Disponibilité", ind["availability"]), use_container_width=True)
    c2.plotly_chart(make_gauge("Performance", ind["performance"]), use_container_width=True)
    c3.plotly_chart(make_gauge("Qualité", ind["quality"]), use_container_width=True)
    c4.plotly_chart(make_gauge("TRS (OEE)", ind["trs"]), use_container_width=True)

    st.subheader("Synthèse")
    st.info(report["summary_text"])

    st.subheader("Recommandations")
    for i, advice in enumerate(report["advices"], 1):
        st.markdown(f"**{i}.** {advice}")
