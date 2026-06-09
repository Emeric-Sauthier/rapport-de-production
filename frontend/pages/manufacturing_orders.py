import streamlit as st

from frontend.utils.api import fetch_orders, import_orders_csv
from frontend.utils.ui import render_orders_table, order_form_dialog

st.title("Ordres de fabrication")

col_upload, col_space, col_btn = st.columns([6, 3, 2])
# col_title.write("")
# uploaded = col_upload.file_uploader("Importer CSV", type=["csv"], label_visibility="collapsed")
# if col_upload.button("Importer CSV", disabled=uploaded is None):
#     result = import_orders_csv(uploaded)
#     if result is not None:
#         st.success(f"{len(result)} ordres importés.")
#         st.rerun()
if col_btn.button("+ Nouvel OF", type="primary", use_container_width=True):
    order_form_dialog()

orders = fetch_orders()
render_orders_table(orders)
uploaded = st.file_uploader("Importer CSV", type=["csv"], label_visibility="collapsed")
if st.button("Importer CSV", disabled=uploaded is None):
    result = import_orders_csv(uploaded)
    if result is not None:
        st.success(f"{len(result)} ordres importés.")
        st.rerun()