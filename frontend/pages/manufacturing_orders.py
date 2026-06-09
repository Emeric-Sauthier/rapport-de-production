import streamlit as st

from frontend.utils.api import fetch_orders
from frontend.utils.ui import render_orders_table, order_form_dialog

st.title("Ordres de fabrication")

col_title, col_btn = st.columns([8, 2])
col_title.write("")
if col_btn.button("+ Nouvel OF", type="primary", use_container_width=True):
    order_form_dialog()

orders = fetch_orders()
render_orders_table(orders)
