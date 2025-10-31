# app.py

import streamlit as st
from utils import init_state, custom_css

# --- Setup ---
st.set_page_config(
    page_title="Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Initialisierung ---
init_state()
custom_css()

# --- Sidebar Navigation ---
st.sidebar.markdown("<h2 style='font-weight: 700; color: #0F172A;'>Navigation</h2>", unsafe_allow_html=True)
page = st.sidebar.radio(
    "Gehe zu:",
    options=[
        "Dashboard", 
        "Neuer Fall", 
        "Laborparameter", 
        "Laborempfehlungen"
    ],
    index=0
)

# --- Page Routing ---
if page == "Dashboard":
    st.markdown('<div class="max-w-6xl mx-auto py-6">', unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 2.25rem; font-weight: 700; color: #0F172A;'>Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Übersicht über Patientenfälle, Labortests und Empfehlungen</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Beispiel-Kacheln / Übersicht
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Offene Fälle", len(st.session_state.get("cases", [])))
    with col2:
        st.metric("Laborparameter", len(st.session_state.get("lab_tests", [])))
    with col3:
        st.metric("Empfehlungsregeln", len(st.session_state.get("recommendations", [])))

    st.markdown("<p style='color: #64748B;'>Wähle eine Aktion im linken Menü.</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Neuer Fall":
    st.experimental_set_query_params(page="02_Neuer_Fall")
    st.experimental_rerun()

elif page == "Laborparameter":
    st.experimental_set_query_params(page="03_Laborparameter")
    st.experimental_rerun()

elif page == "Laborempfehlungen":
    st.experimental_set_query_params(page="04_Empfehlungen")
    st.experimental_rerun()
