from datetime import date

import streamlit as st

from frontend.utils.api import fetch_orders, fetch_downtimes
from frontend.utils.ui import (
    render_orders_table,
    render_downtimes_table,
    render_kpi_cards,
)


def render_machine_detail(machine_name: str):
    st.header(f"⚙️ {machine_name}")

    today = date.today()
    date_range = st.date_input(
        "Période",
        value=(today, today),
        key=f"date_range_{machine_name}",
    )

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        date_from, date_to = date_range[0], date_range[1]
    elif isinstance(date_range, date):
        date_from = date_to = date_range
    else:
        date_from = date_to = today

    all_orders = fetch_orders()
    all_downtimes = fetch_downtimes()

    orders_m = [o for o in all_orders if o.get("machine") == machine_name]
    downtimes_m = [d for d in all_downtimes if d.get("machine") == machine_name]

    st.subheader("Indicateurs")
    render_kpi_cards(orders_m, downtimes_m, date_from, date_to)

    st.divider()

    st.subheader("Ordres de fabrication")
    render_orders_table(orders_m)

    st.divider()

    st.subheader("Arrêts")
    render_downtimes_table(downtimes_m)
