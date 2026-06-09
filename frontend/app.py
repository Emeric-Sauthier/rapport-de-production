import requests
import streamlit as st
import plotly.graph_objects as go
from url import BACKEND_URL
from frontend.i18n import i18n

if "lang" not in st.session_state:
    st.session_state.lang = "en"

lang = st.selectbox(
    i18n("language"),
    options=["en", "fr"],
    index=0 if st.session_state.lang == "en" else 1
)
st.session_state.lang = lang

st.set_page_config(page_title=i18n("page_title"), layout="wide")
st.title(i18n("page_title"))

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
        st.error(i18n("backend_connection_error"))
        st.stop()

    st.session_state.rows = [
        {
            i18n("machine"): m["machine_name"],
            i18n("produced_pieces"): m["pieces_produced"],
            i18n("rejected_pieces"): m["pieces_rejected"],
            i18n("rejection_rate"): round(m["pieces_rejected"] / m["pieces_produced"] * 100, 1),
            i18n("use_time"): m["usage_time_min"]
        }
        for m in machines
    ]

load_machine_rows()
st.subheader(i18n("machines_data"))
st.dataframe(st.session_state.rows, use_container_width=True)

uploaded_file = st.file_uploader(
    i18n("csv_upload"),
    type=["csv"],
    label_visibility="hidden"
)

# --- Bouton de génération ---
if st.button(i18n("generate_report"), type="primary"):
    with st.spinner("ongoing_report_generation"):
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
                    BACKEND_URL + "/import-csv",
                    files=files,
                    timeout=60
                )
                load_machine_rows()
            else:
                response = requests.post(f"{BACKEND_URL}/report/generate", timeout=60)
            response.raise_for_status()
            st.session_state.report = response.json()
            if uploaded_file:
                st.rerun()
        except requests.exceptions.ConnectionError:
            st.error(i18n("backend_connection_error"))
        except Exception as e:
            st.error(f"{i18n('report_generation_error')} : {e}")

# --- Affichage du rapport ---
if st.session_state.report:
    report = st.session_state.report
    ind = report["global_indicators"]

    st.subheader(i18n("global_indicators"))
    c1, c2, c3, c4 = st.columns(4)
    c1.plotly_chart(make_gauge(i18n("gauge_availability"), ind["availability"]), use_container_width=True)
    c2.plotly_chart(make_gauge(i18n("gauge_performance"), ind["performance"]), use_container_width=True)
    c3.plotly_chart(make_gauge(i18n("gauge_quality"), ind["quality"]), use_container_width=True)
    c4.plotly_chart(make_gauge(i18n("gauge_trs"), ind["trs"]), use_container_width=True)

    st.subheader(i18n("synthesis"))
    st.info(report["summary_text"])

    st.subheader(i18n("recommendations"))
    for i, advice in enumerate(report["advices"], 1):
        st.markdown(f"**{i}.** {advice}")
