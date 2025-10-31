# pages/04_Empfehlungen.py

import streamlit as st
from utils import init_state, custom_css, MTS_CATEGORIES, LABTEST_CATEGORIES, URGENCY_LEVELS, create_recommendation, delete_recommendation
import pandas as pd
import time

# Setup
st.set_page_config(layout="wide", page_title="LabAssist | Empfehlungen konfigurieren")
init_state() 
custom_css()

# --- Datenabruf ---
recommendations = st.session_state.recommendations
lab_tests = st.session_state.lab_tests
diagnoses = st.session_state.diagnoses

# Alle verfügbaren Testcodes
all_test_codes = sorted([t['test_code'] for t in lab_tests])
all_diagnosis_names = sorted([d['diagnosis_name'] for d in diagnoses])


# --- Header Section (Fixed, Bombastisch) ---
st.markdown(f"""
    <div class="main-header">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="width: 48px; height: 48px; background: linear-gradient(to bottom right, #10B981, #059669); border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px -1px rgba(16,185,129,0.3);">
                <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="w-7 h-7 text-white" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0-.33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9A1.65 1.65 0 0 0 10 3.69V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
            </div>
            <div>
                <h1 style="font-size: 2.25rem; font-weight: 700; color: #0F172A; margin-bottom: 0.25rem; margin-top: 0;">Empfehlungen konfigurieren</h1>
                <p style="color: #64748B; font-size: 0.875rem; margin: 0;">Definieren und verwalten Sie die KI-Regelwerke für diagnostikbasierte Laborempfehlungen.</p>
            </div>
        </div>
        <div class="green-button">
            {st.button("Neue Empfehlung erstellen", key="add_new_recommendation", on_click=lambda: st.session_state.new_rec_dialog_open=True)}
        </div>
    </div>
""", unsafe_allow_html=True)

# Platzhalter für den fixed Header
st.markdown('<div class="header-spacer"></div>', unsafe_allow_html=True)


# --- Hauptbereich ---
st.markdown('<div class="max-w-7xl mx-auto py-6">', unsafe_allow_html=True)

st.markdown("---") 

# --- Liste der Empfehlungen ---
st.markdown('<div class="stCard-custom">', unsafe_allow_html=True)
st.markdown('<div class="stCard-header">Aktuelle Empfehlungen</div>', unsafe_allow_html=True)
st.markdown('<div class="stCard-content">', unsafe_allow_html=True)

if not recommendations:
    st.info("Es sind noch keine Empfehlungen hinterlegt. Erstellen Sie die erste Regel!", icon="ℹ️")
else:
    # Sortierung für bessere Übersichtlichkeit
    sorted_recommendations = sorted(recommendations, key=lambda x: (x['diagnosis_name'], x['mts_category']))

    for rec in sorted_recommendations:
        mts_style = f'background-color: {MTS_COLOR_MAP.get(rec["mts_category"], "#94A3B8")};'
        
        st.markdown(f"""
            <div class="stCard-custom" style="padding: 1.5rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <h3 style="margin: 0; font-size: 1.25rem; color: #0F172A;">{rec['diagnosis_name']}</h3>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span class="badge-base" style="{mts_style} color: white;">{rec['mts_category']}</span>
                    </div>
                </div>
                <p style="margin-bottom: 0.75rem; color: #475569;">
                    <span style="font-weight: 600;">Begründung:</span> {rec['rationale']}
                </p>
                
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem;">
                    <p style="margin: 0; font-weight: 600; color: #0F172A;">Empfohlene Tests:</p>
                    {''.join([f'<span class="badge-base bg-blue-100 text-blue-800">{test_code}</span>' for test_code in rec.get('recommended_tests', [])])}
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem;">
                    <p style="margin: 0; font-weight: 600; color: #0F172A;">Pflicht-Tests:</p>
                    {''.join([f'<span class="badge-base bg-red-100 text-red-800">{test_code}</span>' for test_code in rec.get('mandatory_tests', [])])}
                </div>
                 <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem;">
                    <p style="margin: 0; font-weight: 600; color: #0F172A;">Optionale Tests:</p>
                    {''.join([f'<span class="badge-base bg-amber-100 text-amber-800">{test_code}</span>' for test_code in rec.get('optional_tests', [])])}
                </div>
                
                <div style="display: flex; gap: 0.5rem; margin-top: 1.5rem;">
                    <div class="red-button">
                        {st.button("Löschen", key=f"delete_rec_{rec['id']}", help="Empfehlung löschen", type="secondary")}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.session_state[f"delete_rec_{rec['id']}"]:
            delete_recommendation(rec['id'])
            st.toast(f"Empfehlung für '{rec['diagnosis_name']}' ({rec['mts_category']}) gelöscht.", icon="🗑️")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True) # Ende stCard-custom


# --- Neue Empfehlung Dialog (Modal-Simulation) ---
if st.session_state.get('new_rec_dialog_open', False):
    with st.container(): # Simuliert ein Modal
        st.subheader("Neue Empfehlung erstellen")
        
        with st.form(key="new_recommendation_form", clear_on_submit=False):
            # Diagnose
            diagnosis_name = st.selectbox(
                "Verdachtsdiagnose (Basis der Empfehlung)", 
                options=all_diagnosis_names, 
                index=0 if all_diagnosis_names else None,
                help="Wählen Sie eine bestehende Diagnose oder legen Sie eine neue an."
            )
            
            # MTS-Kategorie
            mts_category = st.selectbox(
                "MTS-Kategorie", 
                options=MTS_CATEGORIES, 
                index=MTS_CATEGORIES.index('Gelb'),
                format_func=lambda x: f"● {x}"
            )
            
            # Empfohlene Tests (können optional sein, aber oft die Basis)
            recommended_tests = st.multiselect(
                "Empfohlene Labortests", 
                options=all_test_codes, 
                help="Alle Tests, die für diese Diagnose/MTS-Kategorie grundsätzlich empfohlen werden."
            )
            
            # Pflicht-Tests (Muss-Tests, wenn die Empfehlung angewendet wird)
            mandatory_tests = st.multiselect(
                "Pflicht-Tests (KI-Prüfung)", 
                options=recommended_tests, # Pflicht-Tests müssen Teil der empfohlenen Tests sein
                help="Tests aus der Empfehlung, die UNBEDINGT angefordert werden müssen (KI-Prüfung)."
            )

            # Optionale Tests (können angefordert werden, führen aber nicht zu "unnecessary")
            optional_tests = st.multiselect(
                "Optionale Tests (keine Warnung bei Auswahl)",
                options=[t for t in all_test_codes if t not in recommended_tests],
                help="Zusätzliche Tests, die relevant sein können, aber nicht in der primären Empfehlung enthalten sind und auch keine Warnung bei Auswahl auslösen."
            )
            
            rationale = st.text_area("Begründung der Empfehlung", height=100, 
                                     placeholder="Warum diese Tests für diese Diagnose/MTS-Kategorie relevant sind.")
            
            col_dialog_buttons_1, col_dialog_buttons_2 = st.columns(2)
            with col_dialog_buttons_1:
                if st.form_submit_button("Empfehlung speichern", type="primary"):
                    if diagnosis_name and mts_category and recommended_tests and rationale:
                        # Prüfen, ob Kombination schon existiert
                        if any(r['diagnosis_name'] == diagnosis_name and r['mts_category'] == mts_category for r in recommendations):
                            st.error("Fehler: Eine Empfehlung für diese Diagnose und MTS-Kategorie existiert bereits.")
                        else:
                            new_rec_data = {
                                "diagnosis_name": diagnosis_name,
                                "mts_category": mts_category,
                                "recommended_tests": recommended_tests,
                                "mandatory_tests": mandatory_tests,
                                "optional_tests": optional_tests,
                                "rationale": rationale
                            }
                            create_recommendation(new_rec_data)
                            st.session_state.new_rec_dialog_open = False
                            st.toast(f"Empfehlung für '{diagnosis_name}' hinzugefügt.", icon="✨")
                            st.rerun()
                    else:
                        st.error("Bitte füllen Sie mindestens die Felder Diagnose, MTS-Kategorie, Empfohlene Tests und Begründung aus.")
            with col_dialog_buttons_2:
                if st.form_submit_button("Abbrechen"):
                    st.session_state.new_rec_dialog_open = False
                    st.rerun()

st.markdown('</div>', unsafe_allow_html=True) # Main Container End