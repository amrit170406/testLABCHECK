# utils.py

import streamlit as st

# --- Konstanten ---
MTS_CATEGORIES = ["Rot", "Orange", "Gelb", "Grün", "Blau"]
MTS_COLOR_MAP = {
    "Rot": "background-color: #EF4444;",     # Rot
    "Orange": "background-color: #F97316;",  # Orange
    "Gelb": "background-color: #FACC15;",    # Gelb
    "Grün": "background-color: #22C55E;",    # Grün
    "Blau": "background-color: #3B82F6;"     # Blau
}

LABTEST_CATEGORIES = ["Kardiologie", "Hämatologie", "Infektiologie", "Biochemie", "Sonstige"]
LAB_CATEGORIES_BADGE_MAP = {
    "Kardiologie": "badge-red",
    "Hämatologie": "badge-green",
    "Infektiologie": "badge-blue",
    "Biochemie": "badge-purple",
    "Sonstige": "badge-slate"
}

URGENCY_LEVELS = ["Niedrig", "Mittel", "Hoch"]

# --- Session State Initialisierung ---
def init_state():
    """Initialisiert alle benötigten Session State Variablen."""
    if "step" not in st.session_state:
        st.session_state.step = 0
    if "new_case_data" not in st.session_state:
        st.session_state.new_case_data = {}
    if "selected_tests" not in st.session_state:
        st.session_state.selected_tests = []
    if "current_recommendation" not in st.session_state:
        st.session_state.current_recommendation = None
    if "is_analyzing" not in st.session_state:
        st.session_state.is_analyzing = False
    if "lab_tests" not in st.session_state:
        st.session_state.lab_tests = []  # Liste von Dicts
    if "recommendations" not in st.session_state:
        st.session_state.recommendations = []  # Liste von Dicts
    if "cases" not in st.session_state:
        st.session_state.cases = []  # Gespeicherte Fälle
    if "new_test_dialog_open" not in st.session_state:
        st.session_state.new_test_dialog_open = False
    if "new_rec_dialog_open" not in st.session_state:
        st.session_state.new_rec_dialog_open = False
    if "current_diagnosis_input" not in st.session_state:
        st.session_state.current_diagnosis_input = ""


# --- UI Styling ---
def custom_css():
    """Definiert globale CSS-Stile für Buttons, Alerts, Badges."""
    st.markdown("""
    <style>
    .stCard-custom {
        border: 1px solid #E5E7EB;
        border-radius: 0.75rem;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: white;
    }
    .stCard-header {
        font-weight: 600;
        font-size: 1.125rem;
        margin-bottom: 0.5rem;
        color: #0F172A;
    }
    .stCard-content {
        padding-top: 0.5rem;
    }
    .badge-base {
        padding: 0.15rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-red { background-color: #EF4444; color: white; }
    .badge-green { background-color: #22C55E; color: white; }
    .badge-blue { background-color: #3B82F6; color: white; }
    .badge-purple { background-color: #8B5CF6; color: white; }
    .badge-slate { background-color: #64748B; color: white; }
    .badge-destructive { background-color: #DC2626; color: white; }
    .badge-outline { border: 1px solid #E5E7EB; color: #0F172A; }
    .alert-red { background-color: #FEE2E2; padding: 0.5rem; border-radius: 0.25rem; margin-bottom: 0.5rem; }
    .alert-amber { background-color: #FEF3C7; padding: 0.5rem; border-radius: 0.25rem; margin-bottom: 0.5rem; }
    .alert-green { background-color: #DCFCE7; padding: 0.5rem; border-radius: 0.25rem; margin-bottom: 0.5rem; }
    .alert-blue { background-color: #DBEAFE; padding: 0.5rem; border-radius: 0.25rem; margin-bottom: 0.5rem; }
    .green-button .stButton>button { background-color:#22C55E; color:white; width:100%; border-radius:0.5rem; border:none; padding:0.5rem 1rem;}
    .blue-button .stButton>button { background-color:#3B82F6; color:white; width:100%; border-radius:0.5rem; border:none; padding:0.5rem 1rem;}
    .red-button .stButton>button { background-color:#EF4444; color:white; border:none; border-radius:0.5rem; padding:0.25rem 0.5rem;}
    .mts-dot { width: 1rem; height: 1rem; border-radius: 50%; display: inline-block; margin-right: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)


# --- CRUD Funktionen ---
def create_case(case_data):
    """Speichert einen neuen Fall in session_state."""
    st.session_state.cases.append(case_data)


def create_lab_test(test_data):
    """Legt einen neuen Labortest an."""
    test_data["id"] = max([t.get("id", 0) for t in st.session_state.lab_tests] + [0]) + 1
    st.session_state.lab_tests.append(test_data)


def delete_lab_test(test_id):
    """Löscht einen Labortest nach ID."""
    st.session_state.lab_tests = [t for t in st.session_state.lab_tests if t["id"] != test_id]


def create_recommendation(rec_data):
    """Legt eine neue Empfehlung an."""
    rec_data["id"] = max([r.get("id", 0) for r in st.session_state.recommendations] + [0]) + 1
    st.session_state.recommendations.append(rec_data)


def delete_recommendation(rec_id):
    """Löscht eine Empfehlung nach ID."""
    st.session_state.recommendations = [r for r in st.session_state.recommendations if r["id"] != rec_id]
