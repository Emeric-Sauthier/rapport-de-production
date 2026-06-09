import streamlit as st

from frontend.utils.api import fetch_downtimes, import_downtimes_csv
from frontend.utils.ui import render_downtimes_table, downtime_form_dialog, init_lang
from frontend.i18n import i18n

init_lang()

st.title(i18n("downtime"))

col_upload, col_space, col_btn = st.columns([6, 3, 2])
if col_btn.button("+ " + i18n("new_downtime"), type="primary", use_container_width=True):
    downtime_form_dialog()

downtimes = fetch_downtimes()
render_downtimes_table(downtimes)
uploaded = st.file_uploader(i18n("csv_upload"), type=["csv"], label_visibility="collapsed")
if st.button(i18n("csv_upload"), disabled=uploaded is None):
    result = import_downtimes_csv(uploaded)
    if result is not None:
        st.success(f"{len(result)} " + i18n("imported_downtime"))
        st.rerun()
