from datetime import date, datetime, time

import streamlit as st

from frontend.utils.api import (
    create_order, update_order, delete_order,
    create_downtime, update_downtime, delete_downtime,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_dt(s) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s))
    except Exception:
        return None


def _fmt_dt(dt: datetime | None) -> str:
    if dt is None:
        return "—"
    return dt.strftime("%d/%m/%Y %H:%M")


def _fmt_duration(total_seconds: float) -> str:
    total_seconds = max(0.0, total_seconds)
    h = int(total_seconds // 3600)
    m = int((total_seconds % 3600) // 60)
    return f"{h}h {m:02d}min"


# ---------------------------------------------------------------------------
# Dialogs — formulaires OF
# ---------------------------------------------------------------------------

@st.dialog("Ordre de fabrication")
def order_form_dialog(order: dict | None = None, machine_preset: str | None = None):
    editing = order is not None
    error_box = st.container()

    start_dt = _parse_dt(order["start_time"]) if editing else None
    end_dt = _parse_dt(order["end_time"]) if editing else None

    name = st.text_input(
        "Nom *",
        value=order["name"] if editing else "",
        key="dlg_of_name",
    )
    machine = st.text_input(
        "Machine *",
        value=order["machine"] if editing else (machine_preset or ""),
        key="dlg_of_machine",
    )
    col1, col2 = st.columns(2)
    target_qty = col1.number_input(
        "Qté cible *",
        min_value=0,
        value=order["target_quantity"] if editing else 0,
        key="dlg_of_target",
    )
    produced_qty = col2.number_input(
        "Qté produite",
        min_value=0,
        value=order["produced_quantity"] if editing else 0,
        key="dlg_of_produced",
    )

    st.markdown("**Début \\***")
    col3, col4 = st.columns(2)
    start_date = col3.date_input(
        "Date début",
        value=start_dt.date() if start_dt else date.today(),
        label_visibility="collapsed",
        key="dlg_of_start_date",
    )
    start_time_val = col4.time_input(
        "Heure début",
        value=start_dt.time() if start_dt else time(8, 0),
        label_visibility="collapsed",
        key="dlg_of_start_time",
    )

    st.markdown("**Fin \\***")
    col5, col6 = st.columns(2)
    end_date = col5.date_input(
        "Date fin",
        value=end_dt.date() if end_dt else date.today(),
        label_visibility="collapsed",
        key="dlg_of_end_date",
    )
    end_time_val = col6.time_input(
        "Heure fin",
        value=end_dt.time() if end_dt else time(17, 0),
        label_visibility="collapsed",
        key="dlg_of_end_time",
    )

    if st.button("Enregistrer", type="primary", key="dlg_of_submit"):
        start_combined = datetime.combine(start_date, start_time_val)
        end_combined = datetime.combine(end_date, end_time_val)
        errors = []
        if not name.strip():
            errors.append("Le nom est obligatoire.")
        if not machine.strip():
            errors.append("La machine est obligatoire.")
        if end_combined <= start_combined:
            errors.append("La date de fin doit être postérieure à la date de début.")

        if errors:
            for e in errors:
                error_box.error(e)
        else:
            data = {
                "name": name.strip(),
                "machine": machine.strip(),
                "target_quantity": int(target_qty),
                "produced_quantity": int(produced_qty),
                "start_time": start_combined.isoformat(),
                "end_time": end_combined.isoformat(),
            }
            result = update_order(order["id"], data) if editing else create_order(data)
            if result is not None:
                st.toast("Enregistré avec succès ✓")
                st.rerun()


# ---------------------------------------------------------------------------
# Dialogs — formulaires Arrêt
# ---------------------------------------------------------------------------

@st.dialog("Arrêt")
def downtime_form_dialog(downtime: dict | None = None, machine_preset: str | None = None):
    editing = downtime is not None
    error_box = st.container()

    start_dt = _parse_dt(downtime["start_time"]) if editing else None
    end_dt = _parse_dt(downtime["end_time"]) if editing else None

    cause = st.text_input(
        "Cause *",
        value=downtime["cause"] if editing else "",
        key="dlg_dt_cause",
    )
    machine = st.text_input(
        "Machine *",
        value=downtime["machine"] if editing else (machine_preset or ""),
        key="dlg_dt_machine",
    )

    st.markdown("**Début \\***")
    col1, col2 = st.columns(2)
    start_date = col1.date_input(
        "Date début",
        value=start_dt.date() if start_dt else date.today(),
        label_visibility="collapsed",
        key="dlg_dt_start_date",
    )
    start_time_val = col2.time_input(
        "Heure début",
        value=start_dt.time() if start_dt else time(8, 0),
        label_visibility="collapsed",
        key="dlg_dt_start_time",
    )

    st.markdown("**Fin \\***")
    col3, col4 = st.columns(2)
    end_date = col3.date_input(
        "Date fin",
        value=end_dt.date() if end_dt else date.today(),
        label_visibility="collapsed",
        key="dlg_dt_end_date",
    )
    end_time_val = col4.time_input(
        "Heure fin",
        value=end_dt.time() if end_dt else time(9, 0),
        label_visibility="collapsed",
        key="dlg_dt_end_time",
    )

    if st.button("Enregistrer", type="primary", key="dlg_dt_submit"):
        start_combined = datetime.combine(start_date, start_time_val)
        end_combined = datetime.combine(end_date, end_time_val)
        errors = []
        if not cause.strip():
            errors.append("La cause est obligatoire.")
        if not machine.strip():
            errors.append("La machine est obligatoire.")
        if end_combined <= start_combined:
            errors.append("La date de fin doit être postérieure à la date de début.")

        if errors:
            for e in errors:
                error_box.error(e)
        else:
            data = {
                "cause": cause.strip(),
                "machine": machine.strip(),
                "start_time": start_combined.isoformat(),
                "end_time": end_combined.isoformat(),
            }
            result = update_downtime(downtime["id"], data) if editing else create_downtime(data)
            if result is not None:
                st.toast("Enregistré avec succès ✓")
                st.rerun()


# ---------------------------------------------------------------------------
# Dialogs — confirmations de suppression
# ---------------------------------------------------------------------------

@st.dialog("Supprimer l'ordre de fabrication")
def confirm_delete_order_dialog(order: dict):
    st.write(f"Supprimer l'OF **{order['name']}** (machine : {order['machine']}) ?")
    st.caption("Cette action est irréversible.")
    col1, col2 = st.columns(2)
    if col1.button("Supprimer", type="primary", key="dlg_confirm_del_order"):
        delete_order(order["id"])
        st.toast("OF supprimé")
        st.rerun()
    if col2.button("Annuler", key="dlg_cancel_del_order"):
        st.rerun()


@st.dialog("Supprimer l'arrêt")
def confirm_delete_downtime_dialog(downtime: dict):
    st.write(f"Supprimer l'arrêt **{downtime['cause']}** (machine : {downtime['machine']}) ?")
    st.caption("Cette action est irréversible.")
    col1, col2 = st.columns(2)
    if col1.button("Supprimer", type="primary", key="dlg_confirm_del_dt"):
        delete_downtime(downtime["id"])
        st.toast("Arrêt supprimé")
        st.rerun()
    if col2.button("Annuler", key="dlg_cancel_del_dt"):
        st.rerun()


# ---------------------------------------------------------------------------
# Table des ordres de fabrication
# ---------------------------------------------------------------------------

def render_orders_table(orders: list[dict], machine_preset: str | None = None):
    if not orders:
        st.info("Aucun ordre de fabrication.")
        return

    h = st.columns([2, 2, 1, 1, 2.5, 2, 2, 0.6, 0.6])
    for col, label in zip(h, ["Nom", "Machine", "Cible", "Produit", "Progression", "Début", "Fin", "", ""]):
        col.markdown(f"**{label}**")
    st.divider()

    for order in orders:
        cols = st.columns([2, 2, 1, 1, 2.5, 2, 2, 0.6, 0.6])
        cols[0].write(order["name"])
        cols[1].write(order["machine"])
        cols[2].write(str(order["target_quantity"]))
        cols[3].write(str(order["produced_quantity"]))

        tgt = order["target_quantity"]
        prog = min(order["produced_quantity"] / tgt, 1.0) if tgt > 0 else 0.0
        cols[4].progress(prog, text=f"{int(prog * 100)}%")

        cols[5].write(_fmt_dt(_parse_dt(order.get("start_time"))))
        cols[6].write(_fmt_dt(_parse_dt(order.get("end_time"))))

        if cols[7].button("✏️", key=f"edit_order_{order['id']}"):
            order_form_dialog(order=order, machine_preset=machine_preset)
        if cols[8].button("🗑️", key=f"del_order_{order['id']}"):
            confirm_delete_order_dialog(order=order)


# ---------------------------------------------------------------------------
# Table des arrêts
# ---------------------------------------------------------------------------

def render_downtimes_table(downtimes: list[dict], machine_preset: str | None = None):
    if not downtimes:
        st.info("Aucun arrêt.")
        return

    h = st.columns([2.5, 2, 2, 2, 1.5, 0.6, 0.6])
    for col, label in zip(h, ["Cause", "Machine", "Début", "Fin", "Durée", "", ""]):
        col.markdown(f"**{label}**")
    st.divider()

    for dt in downtimes:
        cols = st.columns([2.5, 2, 2, 2, 1.5, 0.6, 0.6])
        cols[0].write(dt["cause"])
        cols[1].write(dt["machine"])
        cols[2].write(_fmt_dt(_parse_dt(dt.get("start_time"))))
        cols[3].write(_fmt_dt(_parse_dt(dt.get("end_time"))))

        start = _parse_dt(dt.get("start_time"))
        end = _parse_dt(dt.get("end_time"))
        cols[4].write(_fmt_duration((end - start).total_seconds()) if (start and end) else "—")

        if cols[5].button("✏️", key=f"edit_dt_{dt['id']}"):
            downtime_form_dialog(downtime=dt, machine_preset=machine_preset)
        if cols[6].button("🗑️", key=f"del_dt_{dt['id']}"):
            confirm_delete_downtime_dialog(downtime=dt)


# ---------------------------------------------------------------------------
# Cartes KPI machine
# ---------------------------------------------------------------------------

def render_kpi_cards(orders: list[dict], downtimes: list[dict], date_from: date, date_to: date):
    dt_from = datetime.combine(date_from, datetime.min.time())
    dt_to = datetime.combine(date_to, datetime.max.time())
    total_secs = (dt_to - dt_from).total_seconds()
    total_hours = total_secs / 3600

    orders_p = [
        o for o in orders
        if (s := _parse_dt(o.get("start_time"))) and dt_from <= s <= dt_to
    ]
    downtimes_p = [
        d for d in downtimes
        if (s := _parse_dt(d.get("start_time"))) and dt_from <= s <= dt_to
    ]

    dt_total_secs = sum(
        (end - start).total_seconds()
        for d in downtimes_p
        if (start := _parse_dt(d.get("start_time"))) and (end := _parse_dt(d.get("end_time")))
    )
    dt_total_hours = dt_total_secs / 3600

    availability = (total_hours - dt_total_hours) / total_hours * 100 if total_hours > 0 else 0.0
    produced = sum(o["produced_quantity"] for o in orders_p)
    target = sum(o["target_quantity"] for o in orders_p)
    performance = produced / target * 100 if target > 0 else 0.0

    col1, col2, col3 = st.columns(3)
    col1.metric("Disponibilité", f"{availability:.1f}%")
    col2.metric("Qté produite", f"{produced:,}")
    col3.metric("Qté cible", f"{target:,}")

    col4, col5, col6 = st.columns(3)
    col4.metric("Performance", f"{performance:.1f}%")
    col5.metric("Nb arrêts", str(len(downtimes_p)))
    col6.metric("Durée arrêts", _fmt_duration(dt_total_secs))
