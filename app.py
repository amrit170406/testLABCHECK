# app.py

import streamlit as st
from utils import init_state, custom_css, ACTIVITY_SVG, MTS_COLOR_MAP, delete_case, update_case, LABTEST_CATEGORIES, LAB_CATEGORIES_BADGE_MAP, MTS_CATEGORIES
from datetime import datetime

# Setup
st.set_page_config(layout="wide", page_title="LabAssist Dashboard")
init_state() # Stellt sicher, dass alle Session State Variablen initialisiert sind
custom_css()

# --- Datenabruf (aus Session State) ---
cases = st.session_state.patient_cases
lab_tests = st.session_state.lab_tests
recommendations = st.session_state.recommendations # Wird für den Edit-Dialog benötigt

# --- Header Section ---
st.markdown(f"""
    <div class="main-header">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="width: 48px; height: 48px; background: linear-gradient(to bottom right, #3B82F6, #2563EB); border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                {ACTIVITY_SVG}
            </div>
            <div>
                <h1 style="font-size: 2.25rem; font-weight: 700; color: #0F172A; margin-bottom: 0.25rem; margin-top: 0;">LabAssist</h1>
                <p style="color: #64748B; font-size: 0.875rem; margin: 0;">Intelligente Laboranforderungen für die Notaufnahme</p>
            </div>
        </div>
        <div class="blue-button">
            {st.button("Neuer Fall", key="new_case_button_header", use_container_width=False, on_click=lambda: st.switch_page("pages/02_Neuer_Fall.py"))}
        </div>
    </div>
""", unsafe_allow_html=True)


# --- Dashboard Hauptbereich ---
# Verwende st.container für eine bessere Struktur und um das max-width zu simulieren
with st.container(border=False):
    st.markdown('<div class="max-w-7xl mx-auto py-0">', unsafe_allow_html=True)

    # --- Stats Calculation ---
    stats = {
        "totalCases": len(cases),
        "averageTests": (sum(len(c.get('ordered_tests', [])) for c in cases) / len(cases) if len(cases) > 0 else 0),
        "casesWithWarnings": sum(1 for c in cases if c.get('missing_tests', []) or c.get('unnecessary_tests', [])),
        "avgDuration": (sum(c.get('estimated_total_duration', 0) for c in cases) / len(cases) if len(cases) > 0 else 0)
    }

    # --- Stats Cards Section (4 Columns) ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-title">Fälle gesamt</p>
            <p class="stat-value">{stats['totalCases']}</p>
            <div class="stat-icon" style="background-color: #DBEAFE;">
                <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="w-6 h-6 text-blue-600" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-title">Ø Tests/Fall</p>
            <p class="stat-value">{stats['averageTests']:.1f}</p>
            <div class="stat-icon" style="background-color: #D1FAE5;">
                <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="w-6 h-6 text-green-600" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-title">Ø Labordauer</p>
            <p class="stat-value">{stats['avgDuration']:.0f} min</p>
            <p style="font-size: 0.75rem; color: #94A3B8; margin-top: 0.25rem;">Bis Ergebnisse vorliegen</p>
            <div class="stat-icon" style="background-color: #FEF3C7;">
                <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="w-6 h-6 text-amber-600" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-title">Fälle mit Hinweisen</p>
            <p class="stat-value">{stats['casesWithWarnings']}</p>
            <div class="stat-icon" style="background-color: #FEE2E2;">
                <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="w-6 h-6 text-red-600" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- Recent Cases Section (Card) ---
    st.markdown('<div class="stCard-custom">', unsafe_allow_html=True)
    st.markdown('<div class="stCard-header">Letzte Fälle</div>', unsafe_allow_html=True)
    st.markdown('<div class="stCard-content">', unsafe_allow_html=True)

    if not cases:
        st.markdown("""
            <div style="text-align: center; padding: 3rem 0;">
                <div style="width: 64px; height: 64px; background-color: #F1F5F9; border-radius: 9999px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto;">
                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="w-8 h-8 text-slate-400" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                </div>
                <p style="color: #64748B; margin-bottom: 1rem;">Noch keine Fälle erfasst</p>
                <div class="blue-button">
                    {st.button("Ersten Fall anlegen", key="first_case_button", on_click=lambda: st.switch_page("pages/02_Neuer_Fall.py"))}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        sorted_cases = sorted(cases, key=lambda x: datetime.fromisoformat(x['created_date']), reverse=True)
        
        for case_item in sorted_cases:
            mts_style = MTS_COLOR_MAP.get(case_item['mts_category'], 'background-color: #94A3B8;')
            
            # Determine Quality Status
            has_warnings = bool(case_item.get('missing_tests') or case_item.get('unnecessary_tests'))
            quality_text = "Hinweise vorhanden" if has_warnings else "Vollständig"
            quality_color = "#D97706" if has_warnings else "#16A34A" # Amber-700 vs Green-700

            st.markdown(f'<div class="case-item">', unsafe_allow_html=True)
            col_info, col_date_buttons = st.columns([0.7, 0.3]) # Angepasste Spaltenbreite

            with col_info:
                st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                        <div class="mts-dot" style="{mts_style}"></div>
                        <span style="font-weight: 600; color: #0F172A;">Fall {case_item.get('case_number', 'N/A')}</span>
                        <span style="color: #64748B;">|</span>
                        <span style="color: #475569;">Pat. {case_item.get('patient_number', 'N/A')}</span>
                        <span style="color: #64748B;">|</span>
                        <span style="color: #475569;">{case_item.get('suspected_diagnosis', 'N/A')}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Details Grid
                col_d1, col_d2, col_d3 = st.columns(3)
                with col_d1:
                    st.markdown(f"""
                        <p style="color: #64748B; margin-bottom: 0.25rem; font-size: 0.875rem;">Alter / Geschlecht</p>
                        <p style="font-weight: 600; color: #0F172A; font-size: 0.875rem;">{case_item.get('age', 'N/A')} / {case_item.get('gender', 'N/A')}</p>
                    """, unsafe_allow_html=True)
                with col_d2:
                    st.markdown(f"""
                        <p style="color: #64748B; margin-bottom: 0.25rem; font-size: 0.875rem;">Angeforderte Tests</p>
                        <p style="font-weight: 600; color: #0F172A; font-size: 0.875rem;">{len(case_item.get('ordered_tests', []))} Tests</p>
                    """, unsafe_allow_html=True)
                with col_d3:
                    # Statt expander, der in der Spalte zu viel Platz braucht, eine Hover-ähnliche Info
                    # Streamlit bietet keine native Hover-Funktion, also halten wir es bei Text/Badges
                    st.markdown(f"""
                        <p style="color: #64748B; margin-bottom: 0.25rem; font-size: 0.875rem;">Qualität</p>
                        <p style="font-weight: 600; color: {quality_color}; font-size: 0.875rem;">{quality_text}</p>
                    """, unsafe_allow_html=True)

            with col_date_buttons:
                st.markdown(f'<p style="text-align: right; color: #64748B; font-size: 0.75rem;">{datetime.fromisoformat(case_item["created_date"]).strftime("%d.%m.%Y, %H:%M")}</p>', unsafe_allow_html=True)
                col_edit_btn, col_delete_btn = st.columns(2)
                with col_edit_btn:
                    if st.button("Edit", key=f"edit_{case_item['id']}", help="Fall bearbeiten", use_container_width=True):
                        st.session_state.edit_case_id = case_item['id']
                        st.session_state.edit_dialog_open = True
                        st.rerun()
                with col_delete_btn:
                    if st.button("🗑️", key=f"delete_{case_item['id']}", help="Fall löschen", use_container_width=True, type="secondary"):
                        delete_case(case_item['id'])
                        st.toast(f"Fall {case_item['case_number']} gelöscht.", icon="✅")
                        st.rerun()
            
            # Additional warnings below for more detail (like the image)
            if has_warnings:
                if case_item.get('missing_tests'):
                    st.markdown(f"""
                        <div class="alert-red" style="margin-top: 1rem;">
                            <p style='margin:0; font-size: 0.875rem;'>
                                <span style="font-weight: 600;">Fehlende Pflicht-Tests:</span> 
                                <span style="margin-left: 0.5rem;">{', '.join(case_item['missing_tests'])}</span>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                if case_item.get('unnecessary_tests'):
                    st.markdown(f"""
                        <div class="alert-amber">
                            <p style='margin:0; font-size: 0.875rem;'>
                                <span style="font-weight: 600;">Möglicherweise überflüssig:</span> 
                                <span style="margin-left: 0.5rem;">{', '.join(case_item['unnecessary_tests'])}</span>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True) # End case item container

    st.markdown('</div>', unsafe_allow_html=True) # End Recent Cases Content
    st.markdown('</div>', unsafe_allow_html=True) # End Recent Cases Card


    # --- Quick Links Section ---
    st.markdown('<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1.5rem; margin-top: 2rem;">', unsafe_allow_html=True)

    # Laborparameter verwalten
    with st.container(): # Simuliert die link-card-blue
        if st.button(
            "Laborparameter verwalten\n\nÜbersicht aller verfügbaren Labortests und deren Eigenschaften",
            key="manage_lab_tests",
            use_container_width=True,
            on_click=lambda: st.switch_page("pages/03_Laborparameter.py"),
            type="secondary" # Kann 'primary' oder 'secondary' sein, um Stil zu ändern
        ): pass
        st.markdown("""
        <style>
        div[data-testid="stButton"] > button[key="manage_lab_tests"] {
            background: linear-gradient(to bottom right, #3B82F6, #2563EB);
            color: white;
            border-radius: 0.75rem;
            box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3), 0 4px 6px -2px rgba(37, 99, 235, 0.15);
            padding: 1.5rem;
            text-align: left;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            justify-content: center;
            line-height: 1.5;
        }
        div[data-testid="stButton"] > button[key="manage_lab_tests"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 20px -5px rgba(37, 99, 235, 0.4), 0 6px 8px -3px rgba(37, 99, 235, 0.2);
        }
        div[data-testid="stButton"] > button[key="manage_lab_tests"] > p {
            font-size: 1.25rem; /* h3 */
            font-weight: 700; /* font-bold */
            color: white;
            margin-bottom: 0.5rem;
            margin-top: 0;
            white-space: pre-wrap; /* Zeilenumbrüche im Text behalten */
        }
        div[data-testid="stButton"] > button[key="manage_lab_tests"] > div > span {
            color: #BFDBFE; /* p-text */
            font-size: 1rem;
            white-space: pre-wrap; /* Zeilenumbrüche im Text behalten */
        }
        </style>
        """, unsafe_allow_html=True)

    # Empfehlungen konfigurieren
    with st.container(): # Simuliert die link-card-green
        if st.button(
            "Empfehlungen konfigurieren\n\nRegelwerk für diagnostikbasierte Laborempfehlungen pflegen",
            key="configure_recommendations",
            use_container_width=True,
            on_click=lambda: st.switch_page("pages/04_Empfehlungen.py"),
            type="secondary" # Kann 'primary' oder 'secondary' sein, um Stil zu ändern
        ): pass
        st.markdown("""
        <style>
        div[data-testid="stButton"] > button[key="configure_recommendations"] {
            background: linear-gradient(to bottom right, #10B981, #059669);
            color: white;
            border-radius: 0.75rem;
            box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3), 0 4px 6px -2px rgba(16, 185, 129, 0.15);
            padding: 1.5rem;
            text-align: left;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            justify-content: center;
            line-height: 1.5;
        }
        div[data-testid="stButton"] > button[key="configure_recommendations"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 20px -5px rgba(16, 185, 129, 0.4), 0 6px 8px -3px rgba(16, 185, 129, 0.2);
        }
        div[data-testid="stButton"] > button[key="configure_recommendations"] > p {
            font-size: 1.25rem; /* h3 */
            font-weight: 700; /* font-bold */
            color: white;
            margin-bottom: 0.5rem;
            margin-top: 0;
            white-space: pre-wrap;
        }
        div[data-testid="stButton"] > button[key="configure_recommendations"] > div > span {
            color: #D1FAE5; /* p-text */
            font-size: 1rem;
            white-space: pre-wrap;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # End Quick Links Grid
    st.markdown('</div>', unsafe_allow_html=True) # Main Container End


# --- Edit Dialog (Simulated Modal mit st.form) ---
if st.session_state.get('edit_dialog_open', False) and st.session_state.get('edit_case_id'):
    case_id = st.session_state.edit_case_id
    current_case = next((c for c in cases if c['id'] == case_id), None)

    if current_case:
        # Ein expander simuliert ein Modal halbwegs, kann aber auch direkt im Hauptbereich angezeigt werden
        # Für eine bessere Modal-Simulation könnte man st.empty() und dann einen Container verwenden
        st.subheader("Fall bearbeiten")
        
        with st.form(key="edit_case_form", clear_on_submit=False):
            st.markdown("---") # Trennlinie für bessere Optik

            # Fallnummer ist nicht bearbeitbar
            st.text_input("Fallnummer", value=current_case.get('case_number', 'N/A'), disabled=True)

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                edited_patient_number = st.text_input("Patientennummer", value=current_case.get('patient_number', ''), key="edit_patient_number")
                edited_age = st.number_input("Alter (Jahre)", min_value=0, max_value=120, value=current_case.get('age', 35), step=1, key="edit_age")
            with col_p2:
                edited_gender_options = ['Männlich', 'Weiblich', 'Divers']
                edited_gender = st.selectbox("Geschlecht", options=edited_gender_options, index=edited_gender_options.index(current_case.get('gender', 'Männlich')), key="edit_gender")
                
                edited_mts_category = st.selectbox("MTS-Kategorie", options=MTS_CATEGORIES, index=MTS_CATEGORIES.index(current_case.get('mts_category', 'Blau')), key="edit_mts_category")

            edited_suspected_diagnosis = st.text_input("Verdachtsdiagnose", value=current_case.get('suspected_diagnosis', ''), key="edit_suspected_diagnosis")
            
            # Alle verfügbaren Test-Codes für Multiselect
            all_lab_test_codes = [t['test_code'] for t in lab_tests]
            edited_ordered_tests = st.multiselect(
                "Angeforderte Tests",
                options=all_lab_test_codes,
                default=current_case.get('ordered_tests', []),
                key="edit_ordered_tests"
            )

            # --- Vitalparameter bearbeiten ---
            st.markdown("#### Vitalparameter")
            current_vitals = current_case.get('vitals', {})
            col_v1_edit, col_v2_edit = st.columns(2)
            with col_v1_edit:
                edited_blood_pressure = st.text_input("Blutdruck (mmHG)", value=current_vitals.get('blood_pressure', ''), key="edit_bp")
                edited_temperature = st.number_input("Temperatur (°C)", min_value=30.0, max_value=42.0, value=current_vitals.get('temperature', 36.8), step=0.1, format="%.1f", key="edit_temp")
                edited_heart_rate = st.number_input("Herzfrequenz (bpm)", min_value=30, max_value=200, value=current_vitals.get('heart_rate', 75), step=1, key="edit_hr")
            with col_v2_edit:
                edited_respiratory_rate = st.number_input("Atemfrequenz (/min)", min_value=5, max_value=50, value=current_vitals.get('respiratory_rate', 16), step=1, key="edit_rr")
                edited_oxygen_saturation = st.number_input("Sauerstoffsättigung (%)", min_value=50, max_value=100, value=current_vitals.get('oxygen_saturation', 98), step=1, key="edit_o2")
                edited_blood_sugar = st.number_input("Blutzucker (mg/dl)", min_value=30, max_value=500, value=current_vitals.get('blood_sugar', 110), step=1, key="edit_bs")

            col_dialog_buttons_1, col_dialog_buttons_2 = st.columns(2)
            with col_dialog_buttons_1:
                if st.form_submit_button("Speichern", type="primary"):
                    # Recalculate quality metrics based on updated selection
                    matching_rec = next((
                        r for r in recommendations 
                        if r['diagnosis_name'].lower() == edited_suspected_diagnosis.lower() and 
                           r['mts_category'] == edited_mts_category
                    ), None)

                    missing = []
                    unnecessary = []
                    max_duration = 0

                    if matching_rec:
                        mandatory_tests = matching_rec.get('mandatory_tests', [])
                        recommended_set = set(matching_rec.get('recommended_tests', []))
                        optional_test_codes = set(matching_rec.get('optional_tests', []))

                        missing = [t for t in mandatory_tests if t not in edited_ordered_tests]
                        unnecessary = [t for t in edited_ordered_tests if t not in recommended_set and t not in optional_test_codes]
                    
                    if edited_ordered_tests:
                        max_duration = max([t['estimated_duration_minutes'] for t in lab_tests if t['test_code'] in edited_ordered_tests], default=0)

                    updated_data = {
                        "patient_number": edited_patient_number,
                        "age": edited_age,
                        "gender": edited_gender,
                        "mts_category": edited_mts_category,
                        "suspected_diagnosis": edited_suspected_diagnosis,
                        "ordered_tests": edited_ordered_tests,
                        "missing_tests": missing,
                        "unnecessary_tests": unnecessary,
                        "estimated_total_duration": max_duration,
                        "vitals": {
                            "blood_pressure": edited_blood_pressure,
                            "temperature": edited_temperature,
                            "heart_rate": edited_heart_rate,
                            "respiratory_rate": edited_respiratory_rate,
                            "oxygen_saturation": edited_oxygen_saturation,
                            "blood_sugar": edited_blood_sugar
                        }
                    }
                    update_case(case_id, updated_data)
                    st.session_state.edit_dialog_open = False
                    st.toast(f"Fall {current_case['case_number']} aktualisiert.", icon="👍")
                    st.rerun()
            with col_dialog_buttons_2:
                if st.form_submit_button("Abbrechen"):
                    st.session_state.edit_dialog_open = False
                    st.rerun()