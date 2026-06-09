import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"


def _get(path: str):
    try:
        resp = requests.get(f"{BACKEND_URL}{path}", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("Impossible de joindre le backend sur http://localhost:8000.")
        return None
    except Exception as e:
        st.error(f"Erreur API ({path}) : {e}")
        return None


def _post_file(path: str, file):
    try:
        files = {"file": (file.name, file.getvalue(), "text/csv")}
        resp = requests.post(f"{BACKEND_URL}{path}", files=files, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("Impossible de joindre le backend.")
        return None
    except Exception as e:
        st.error(f"Erreur API ({path}) : {e}")
        return None


def _post(path: str, data: dict):
    try:
        resp = requests.post(f"{BACKEND_URL}{path}", json=data, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("Impossible de joindre le backend.")
        return None
    except Exception as e:
        st.error(f"Erreur API ({path}) : {e}")
        return None


def _put(path: str, data: dict):
    try:
        resp = requests.put(f"{BACKEND_URL}{path}", json=data, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("Impossible de joindre le backend.")
        return None
    except Exception as e:
        st.error(f"Erreur API ({path}) : {e}")
        return None


def _delete(path: str) -> bool:
    try:
        resp = requests.delete(f"{BACKEND_URL}{path}", timeout=5)
        resp.raise_for_status()
        return True
    except requests.exceptions.ConnectionError:
        st.error("Impossible de joindre le backend.")
        return False
    except Exception as e:
        st.error(f"Erreur API ({path}) : {e}")
        return False


def fetch_machines() -> list[dict]:
    return _get("/machines") or []


def fetch_machines_list() -> list[dict]:
    return _get("/machines-list") or []


def fetch_orders() -> list[dict]:
    return _get("/manufacturing-orders") or []


def fetch_downtimes() -> list[dict]:
    return _get("/downtimes") or []


def create_order(data: dict):
    return _post("/manufacturing-orders", data)


def update_order(order_id: str, data: dict):
    return _put(f"/manufacturing-orders/{order_id}", data)


def delete_order(order_id: str) -> bool:
    return _delete(f"/manufacturing-orders/{order_id}")


def create_downtime(data: dict):
    return _post("/downtimes", data)


def update_downtime(dt_id: str, data: dict):
    return _put(f"/downtimes/{dt_id}", data)


def delete_downtime(dt_id: str) -> bool:
    return _delete(f"/downtimes/{dt_id}")


def import_orders_csv(file):
    return _post_file("/import-csv/manufacturing-orders", file)


def import_downtimes_csv(file):
    return _post_file("/import-csv/downtimes", file)
