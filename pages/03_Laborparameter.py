# pages/03_Laborparameter.py

import streamlit as st
from utils import init_state, custom_css, LABTEST_CATEGORIES, URGENCY_LEVELS, create_lab_test, delete_lab_test, LAB_CATEGORIES_BADGE_MAP
import pandas as pd
import time

# Setup
st.set_page_config(layout="wide", page_title="LabAssist | Laborparameter verwalten")
init_state() 
custom_css()

# --- Datenabruf ---
lab_tests = st.session_state.lab_tests

# --- Header Section (Fixed, Bombastisch) ---
st.markdown(f"""
    <div class="main-header">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="width: 48px; height: 48px; background: linear-gradient(to bottom right, #3B82F6, #2563EB); border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="w-7 h-7 text-white" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
            </div>
            <div>
                <h1 style="font-size: 2.25rem; font-weight: 700; color: #0F172A; margin-bottom: 0.25rem; margin-top: 0;">Laborparameter verwalten</h1>
                <p style="color: #64748B; font-size: 0.875rem; margin: 0;">Übersicht aller verfügbaren Labortests und deren Eigenschaften</p>
            </div>
        </div>
        <div class="blue-button">
            {st.button("Neuen Labortest hinzufügen", key="add_new_labtest", on_click=lambda: st.session_state.update(new_test_dialog_open=True, edit_test_data=None))}
        </div>
    </div>
""", unsafe_allow_html=True)

# Platzhalter für den fixed Header
st.markdown('<div class="header-spacer"></div>', unsafe_allow_html=True)


# --- Hauptbereich ---
st.markdown('<div class="max-w-7xl mx-auto py-6">', unsafe_allow_html=True)


st.markdown("---") 

# --- Liste der Labortests (Dataframe oder individuelle Darstellung) ---
st.markdown('<div class="stCard-custom">', unsafe_allow_html=True)
st.markdown('<div class="stCard-header">Aktuelle Laborparameter</div>', unsafe_allow_html=True)
st.markdown('<div class="stCard-content">', unsafe_allow_html=True)

if not lab_tests:
    st.info("Es sind noch keine Laborparameter hinterlegt. Fügen Sie den ersten Test hinzu!", icon="ℹ️")
else:
    # Optionale Anzeige als Tabelle für Übersichtlichkeit, aber detaillierte Ansicht auch möglich
    df_lab_tests = pd.DataFrame(lab_tests)
    df_lab_tests = df_lab_tests.drop(columns=['id']) # ID nicht anzeigen
    
    # Spalten umbenennen für bessere Lesbarkeit
    df_lab_tests.columns = [
        "Testname", "Testcode", "Kategorie", "Dauer (min)", "Dringlichkeit", "Einheit", "Normalbereich"
    ]
    
    st.dataframe(df_lab_tests, 
                 use_container_width=True, 
                 hide_index=True,
                 column_config={
                     "Kategorie": st.column_config.Column(
                         "Kategorie",
                         help="Kategorie des Labortests",
                         width="medium"
                     ),
                     "Dringlichkeit": st.column_config.Column(
                         "Dringlichkeit",
                         help="Standard-Dringlichkeitsstufe",
                         width="small"
                     ),
                     "Dauer (min)": st.column_config.NumberColumn(
                         "Dauer (min)",
                         help="Geschätzte Dauer bis Ergebnis (Minuten)",
                         format="%d",
                         width="small"
                     )
                 })
    
    st.markdown("---")
    st.markdown("#### Detaillierte Ansicht & Aktionen")

    for test in lab_tests:
        badge_class = LAB_CATEGORIES_BADGE_MAP.get(test['category'], 'bg-gray-100 text-gray-800')
        st.markdown(f"""
            <div class="stCard-custom" style="padding: 1.5rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <h3 style="margin: 0; font-size: 1.25rem; color: #0F172A;">{test['test_name']} ({test['test_code']})</h3>
                    <div style="display: flex; gap: 0.5rem;">
                        <span class="badge-base {badge_class}">{test['category']}</span>
                        <span class="badge-base bg-blue-100 text-blue-800">{test['urgency_level']}</span>
                    </div>
                </div>
                <p style="margin-bottom: 0.5rem; color: #475569;">Dauer: {test['estimated_duration_minutes']} min | Einheit: {test['unit']} | Normalbereich: {test['normal_range']}</p>
                
                <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
                    <div class="red-button">
                        {st.button("Löschen", key=f"delete_test_{test['id']}", help="Labortest löschen", type="secondary")}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.session_state[f"delete_test_{test['id']}"]:
            delete_lab_test(test['id'])
            st.toast(f"Labortest '{test['test_name']}' gelöscht.", icon="🗑️")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True) # Ende stCard-custom


# --- Neuer Labortest Dialog (Modal-Simulation) ---
if st.session_state.get('new_test_dialog_open', False):
    with st.container(): # Simuliert ein Modal
        st.subheader("Neuen Labortest hinzufügen")
        
        with st.form(key="new_lab_test_form", clear_on_submit=False):
            test_name = st.text_input("Testname", placeholder="z.B. Troponin T")
            test_code = st.text_input("Testcode (eindeutig, kurz)", placeholder="z.B. TROP")
            
            col_cat, col_urgency = st.columns(2)
            with col_cat:
                category = st.selectbox("Kategorie", options=LABTEST_CATEGORIES)
            with col_urgency:
                urgency_level = st.selectbox("Standard-Dringlichkeit", options=URGENCY_LEVELS)
            
            col_duration, col_unit = st.columns(2)
            with col_duration:
                estimated_duration_minutes = st.number_input("Geschätzte Dauer bis Ergebnis (Minuten)", min_value=5, max_value=240, value=30, step=5)
            with col_unit:
                unit = st.text_input("Einheit", placeholder="z.B. ng/ml, mg/L")
            
            normal_range = st.text_input("Normalbereich", placeholder="z.B. 0-14, <5")
            
            col_dialog_buttons_1, col_dialog_buttons_2 = st.columns(2)
            with col_dialog_buttons_1:
                if st.form_submit_button("Test speichern", type="primary"):
                    if test_name and test_code and unit and normal_range:
                        # Prüfen, ob Testcode bereits existiert
                        if any(t['test_code'] == test_code for t in lab_tests):
                            st.error(f"Fehler: Ein Labortest mit dem Code '{test_code}' existiert bereits.")
                        else:
                            new_test_data = {
                                "test_name": test_name,
                                "test_code": test_code.upper(), # Testcodes oft GROSS
                                "category": category,
                                "estimated_duration_minutes": estimated_duration_minutes,
                                "urgency_level": urgency_level,
                                "unit": unit,
                                "normal_range": normal_range
                            }
                            create_lab_test(new_test_data)
                            st.session_state.new_test_dialog_open = False
                            st.toast(f"Labortest '{test_name}' hinzugefügt.", icon="➕")
                            st.rerun()
                    else:
                        st.error("Bitte füllen Sie alle Felder aus.")
            with col_dialog_buttons_2:
                if st.form_submit_button("Abbrechen"):
                    st.session_state.new_test_dialog_open = False
                    st.rerun()

st.markdown('</div>', unsafe_allow_html=True) # Main Container End