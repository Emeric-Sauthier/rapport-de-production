import streamlit as st
from url import BACKEND_URL

TRANSLATIONS = {
    "en": {
        "language": "Language",
        "page_title": "Industrial Production Report",
        "backend_connection_error": f"Cannot connect to backend on {BACKEND_URL}. Check if it's running.",
        "machine": "Machine",
        "produced_pieces": "Produced pieces",
        "rejected_pieces": "Rejected pieces",
        "rejection_rate": "Rejection rate (%)",
        "use_time": "Use time (min)",
        "machines_data": "Machines data",
        "csv_upload": "Choose a CSV file",
        "generate_report": "Generate the report",
        "ongoing_report_generation": "Generating the report...",
        "report_generation_error": "Error while generating the report",
        "global_indicators": "Global indicators",
        "gauge_availability": "Availability",
        "gauge_performance": "Performance",
        "gauge_quality": "Quality",
        "gauge_trs": "TRS (OEE)",
        "synthesis": "Synthesis",
        "recommendations": "Recommendations"
    },
    "fr": {
        "language": "Langue",
        "page_title": "Rapport de Production Industrielle",
        "backend_connection_error": f"Impossible de joindre le backend sur {BACKEND_URL}. Vérifiez qu'il est démarré.",
        "machine": "Machine",
        "produced_pieces": "Pièces produites",
        "rejected_pieces": "Pièces rejetées",
        "rejection_rate": "Taux de rejet (%)",
        "use_time": "Temps d'utilisation (min)",
        "machines_data": "Données machines",
        "csv_upload": "Choisir un fichier CSV",
        "generate_report": "Générer le rapport",
        "ongoing_report_generation": "Génération du rapport en cours...",
        "report_generation_error": "Erreur lors de la génération du rapport",
        "global_indicators": "Indicateurs globaux",
        "gauge_availability": "Disponibilité",
        "gauge_performance": "Performance",
        "gauge_quality": "Qualité",
        "gauge_trs": "TRS (OEE)",
        "synthesis": "Synthèse",
        "recommendations": "Recommandations"
    }
}

def i18n(key):
    return TRANSLATIONS[st.session_state.lang][key]
