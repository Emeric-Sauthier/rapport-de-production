import streamlit as st

from frontend.utils.api import fetch_downtimes, import_downtimes_csv
from frontend.utils.ui import render_downtimes_table, downtime_form_dialog

st.title("Arrêts")

col_upload, col_space, col_btn = st.columns([6, 3, 2])
# col_title.write("")
uploaded = col_upload.file_uploader("Importer CSV", type=["csv"], label_visibility="collapsed")
if col_upload.button("Importer CSV", disabled=uploaded is None):
    result = import_downtimes_csv(uploaded)
    if result is not None:
        st.success(f"{len(result)} arrêts importés.")
        st.rerun()
if col_btn.button("+ Nouvel Arrêt", type="primary", use_container_width=True):
    downtime_form_dialog()

downtimes = fetch_downtimes()
render_downtimes_table(downtimes)
