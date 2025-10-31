# pages/03_Laborparameter.py

import streamlit as st
from utils import init_state, custom_css, LABTEST_CATEGORIES, URGENCY_LEVELS, create_lab_test, delete_lab_test, LAB_CATEGORIES_BADGE_MAP
import time

# Setup
st.set_page_config(layout="wide", page_title="Laborparameter")
init_state() # Stellt sicher, dass alle Session State Variablen initialisiert sind
custom_css()

# --- Datenabruf (aus Session State) ---
_lab_tests = st.session_state.lab_tests

# --- UI Layout ---
st.markdown('<div class="max-w-7xl mx-auto py-6">', unsafe_allow_html=True) # Main Container

st.page_link("app.py", label="Zurück zum Dashboard", icon="home") # Korrektur: "home" als Lucide Icon

col_header_1, col_header_2 = st.columns([3, 1])

with col_header_1:
    st.markdown("<h1 style='font-size: 2.25rem; font-weight: 700; color: #0F172A;'>Laborparameter</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Verwaltung aller verfügbaren Labortests</p>", unsafe_allow_html=True)

with col_header_2:
    if st.button("Neuer Test anlegen", key="new_test_button", use_container_width=True, type="primary"):
        st.session_state.new_test_dialog_open = True
   

# --- New Test Dialog (Form) ---
if st.session_state.get('new_test_dialog_open', False):
    with st.form(key="new_lab_test_form"):
        st.markdown("### Neuen Labortest anlegen")

        new_test_name = st.text_input("Testname", placeholder="z.B. Troponin T")
        new_test_code = st.text_input("Test-Code", placeholder="z.B. TROP")
        new_category = st.selectbox("Kategorie", options=LABTEST_CATEGORIES, index=1)
        new_duration = st.number_input("Geschätzte Dauer (Minuten)", min_value=5, max_value=240, value=30, step=5)
        new_urgency = st.selectbox("Dringlichkeit", options=URGENCY_LEVELS, index=0)
        new_unit = st.text_input("Einheit", placeholder="z.B. ng/ml")
        new_normal_range = st.text_input("Normalbereich", placeholder="z.B. 0-14")

        col_dialog_buttons_1, col_dialog_buttons_2 = st.columns(2)
        with col_dialog_buttons_1:
            if st.form_submit_button("Speichern", type="primary"):
                if not new_test_name or not new_test_code:
                    st.error("Testname und Test-Code sind Pflichtfelder.")
                else:
                    create_lab_test({
                        "test_name": new_test_name,
                        "test_code": new_test_code,
                        "category": new_category,
                        "estimated_duration_minutes": new_duration,
                        "urgency_level": new_urgency,
                        "unit": new_unit,
                        "normal_range": new_normal_range
                    })
                    st.session_state.new_test_dialog_open = False
                    st.toast(f"Test '{new_test_name}' angelegt.", icon="👍")
                    st.rerun()
        with col_dialog_buttons_2:
            if st.form_submit_button("Abbrechen"):
                st.session_state.new_test_dialog_open = False
                st.rerun()

# --- Tests Display ---
st.markdown('<div class="stCard-custom">', unsafe_allow_html=True)
st.markdown('<div class="stCard-content">', unsafe_allow_html=True)

if not _lab_tests:
    st.markdown("""
        <div style="text-align: center; padding: 3rem 0;">
            <p style="color: #64748B; margin-bottom: 1rem;">Noch keine Labortests angelegt</p>
            <div class="blue-button">
                {st.button("Ersten Test anlegen", key="first_test_button", type="primary")}
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.session_state.get("first_test_button"):
        st.session_state.new_test_dialog_open = True
        st.rerun()
else:
    cols_tests = st.columns(3)
    for i, test in enumerate(_lab_tests): # Greift auf _lab_tests zu
        with cols_tests[i % 3]:
            # Custom Card Styling for Test Item
            st.markdown(f"""
                <div style="border: 1px solid #E2E8F0; border-radius: 0.75rem; padding: 1rem; margin-bottom: 1rem; background-color: white;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                        <div>
                            <p style="font-size: 1.125rem; font-weight: 600; color: #0F172A; margin: 0;">{test['test_name']}</p>
                            <p style="font-size: 0.75rem; color: #64748B; margin: 0.25rem 0 0 0;">{test['test_code']}</p>
                        </div>
                        <div class="red-button">
                            {st.button('🗑️', key=f"delete_test_{test['id']}", help="Test löschen")}
                        </div>
                    </div>
                    <div style="margin-top: 0.75rem;">
                        <span class="badge-base {LAB_CATEGORIES_BADGE_MAP.get(test['category'], 'badge-slate')}">{test['category']}</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; color: #475569; margin-top: 0.5rem;">
                        <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                        <span>{test['estimated_duration_minutes']} min</span>
                    </div>
                    {test.get('unit') and f'<p style="font-size: 0.75rem; color: #64748B; margin: 0.5rem 0 0 0;">Einheit: {test["unit"]}</p>'}
                    {test.get('normal_range') and f'<p style="font-size: 0.75rem; color: #64748B; margin: 0.25rem 0 0 0;">Normal: {test["normal_range"]}</p>'}
                    <span class="badge-base badge-outline" style="margin-top: 0.5rem;">{test['urgency_level']}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Handle Delete Action
            if st.session_state.get(f"delete_test_{test['id']}"):
                delete_lab_test(test['id'])
                st.toast(f"Test '{test['test_name']}' gelöscht.", icon="❌")
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)