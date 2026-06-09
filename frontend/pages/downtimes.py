import streamlit as st

from frontend.utils.api import fetch_downtimes
from frontend.utils.ui import render_downtimes_table, downtime_form_dialog

st.title("Arrêts")

col_title, col_btn = st.columns([8, 2])
col_title.write("")
if col_btn.button("+ Nouvel Arrêt", type="primary", use_container_width=True):
    downtime_form_dialog()

downtimes = fetch_downtimes()
render_downtimes_table(downtimes)
