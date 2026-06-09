import streamlit as st

from frontend.utils.api import fetch_machines, fetch_orders, fetch_downtimes
from frontend.utils.ui import render_orders_table, render_downtimes_table


def render_machine_detail(machine_name: str):
    st.header(f"⚙️ {machine_name}")

    machines = fetch_machines()
    machine_data = next((m for m in machines if m["machine_name"] == machine_name), None)

    st.subheader("Indicateurs")
    if machine_data:
        planned = machine_data["planned_time_min"]
        usage = machine_data["usage_time_min"]
        produced = machine_data["pieces_produced"]
        target = machine_data["pieces_target"]
        rejected = machine_data["pieces_rejected"]

        availability = usage / planned * 100 if planned > 0 else 0.0
        performance = produced / target * 100 if target > 0 else 0.0
        quality = (produced - rejected) / produced * 100 if produced > 0 else 0.0

        col1, col2, col3 = st.columns(3)
        col1.metric("Disponibilité", f"{availability:.1f}%")
        col2.metric("Performance", f"{performance:.1f}%")
        col3.metric("Qualité", f"{quality:.1f}%")

        col4, col5, col6 = st.columns(3)
        col4.metric("Qté produite", f"{produced:,}")
        col5.metric("Qté cible", f"{target:,}")
        col6.metric("Qté rejetée", f"{rejected:,}")
    else:
        st.info("Aucune donnée calculée pour cette machine.")

    st.divider()

    all_orders = fetch_orders()
    all_downtimes = fetch_downtimes()

    orders_m = [o for o in all_orders if o.get("machine") == machine_name]
    downtimes_m = [d for d in all_downtimes if d.get("machine") == machine_name]

    st.subheader("Ordres de fabrication")
    render_orders_table(orders_m, machine_preset=machine_name)

    st.divider()

    st.subheader("Arrêts")
    render_downtimes_table(downtimes_m, machine_preset=machine_name)
