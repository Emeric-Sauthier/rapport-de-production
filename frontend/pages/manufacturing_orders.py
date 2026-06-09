import streamlit as st

from frontend.utils.api import fetch_orders, import_orders_csv
from frontend.utils.ui import render_orders_table, order_form_dialog, init_lang
from frontend.i18n import i18n

init_lang()

st.title(i18n("crafting_orders"))

col_upload, col_space, col_btn = st.columns([6, 3, 2])
if col_btn.button("+ " + i18n("new_crafting_order"), type="primary", use_container_width=True):
    order_form_dialog()

orders = fetch_orders()
render_orders_table(orders)
uploaded = st.file_uploader(i18n("csv_upload"), type=["csv"], label_visibility="collapsed")
if st.button(i18n("csv_upload"), disabled=uploaded is None):
    result = import_orders_csv(uploaded)
    if result is not None:
        st.success(f"{len(result)} " + i18n("imported_orders"))
        st.rerun()