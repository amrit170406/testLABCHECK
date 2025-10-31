# app.py

import streamlit as st
from utils import init_state, custom_css, ACTIVITY_SVG, MTS_COLOR_MAP, delete_case, update_case, LABTEST_CATEGORIES
from datetime import datetime

# Setup
st.set_page_config(layout="wide", page_title="LabAssist Dashboard")
init_state()
custom_css()

# --- Datenabruf ---
cases = st.session_state.patient_cases
lab_tests = st.session_state.lab_tests

# --- Header Section (Custom HTML/CSS) ---
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
            <a href="Neuer_Fall" target="_self" style="text-decoration: none;">
                {st.button("Neuer Fall anlegen", key="new_case_button_header", use_container_width=True)}
            </a>
        </div>
    </div>
""", unsafe_allow_html=True)


st.markdown('<div class="max-w-7xl mx-auto px-6 py-0">', unsafe_allow_html=True) # Main Container Start

# --- Stats Calculation ---
stats = {
    "totalCases": len(cases),
    "averageTests": (sum(len(c.get('ordered_tests', [])) for c in cases) / len(cases) if len(cases) > 0 else 0),
    "casesWithErrors": sum(1 for c in cases if c.get('missing_tests', []) or c.get('unnecessary_tests', [])),
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
        <p class="stat-value">{stats['casesWithErrors']}</p>
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
                <a href="Neuer_Fall" target="_self" style="text-decoration: none;">
                    {st.button("Ersten Fall anlegen", key="first_case_button")}
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    sorted_cases = sorted(cases, key=lambda x: datetime.fromisoformat(x['created_date']), reverse=True)
    
    for case_item in sorted_cases:
        mts_style = MTS_COLOR_MAP.get(case_item['mts_category'], 'background-color: #94A3B8;')
        
        # Determine Quality Status
        has_warnings = bool(case_item.get('missing_tests') or case_item.get('unnecessary_tests'))
        quality_icon = """<svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 text-amber-500" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>""" if has_warnings else """<svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 text-green-500" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><polyline points="20 6 9 17 4 12"></polyline></svg>"""
        quality_text = "Hinweise vorhanden" if has_warnings else "Vollständig"
        quality_color = "#D97706" if has_warnings else "#16A34A"

        # Start the case item container
        st.markdown(f'<div class="case-item" id="{case_item["id"]}">', unsafe_allow_html=True)
        
        col_main, col_actions = st.columns([4, 1])

        # Main Info
        with col_main:
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <div class="w-3 h-3 rounded-full" style="width: 12px; height: 12px; border-radius: 9999px; {mts_style}"></div>
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
                # Use st.expander() to simulate HoverCard for quality details
                with st.expander(f'Qualität: <span style="font-weight: 600; color: {quality_color};">{quality_text}</span>'):
                    if has_warnings:
                        if case_item.get('missing_tests'):
                            st.markdown(f"""
                                <p style='font-size: 0.75rem; font-weight: 600; color: #DC2626; margin-bottom: 0.25rem;'>Fehlende Pflicht-Tests:</p>
                                <div style='display: flex; flex-wrap: wrap; gap: 0.25rem;'>
                                    {''.join([f'<span class="badge-base badge-red">{t}</span>' for t in case_item['missing_tests']])}
                                </div>
                            """, unsafe_allow_html=True)
                        if case_item.get('unnecessary_tests'):
                            st.markdown(f"""
                                <p style='font-size: 0.75rem; font-weight: 600; color: #D97706; margin-top: 0.5rem; margin-bottom: 0.25rem;'>Möglicherweise überflüssig:</p>
                                <div style='display: flex; flex-wrap: wrap; gap: 0.25rem;'>
                                    {''.join([f'<span class="badge-base badge-amber">{t}</span>' for t in case_item['unnecessary_tests']])}
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown('<p style="font-size: 0.875rem; color: #16A34A;">Der angeforderte Testsatz entspricht den Empfehlungen.</p>', unsafe_allow_html=True)

        # Actions
        with col_actions:
            col_edit, col_delete = st.columns(2)
            with col_edit:
                # Bearbeiten-Button ist jetzt ein echter Button
                if st.button("Edit", key=f"edit_{case_item['id']}", help="Fall bearbeiten", use_container_width=True):
                    st.session_state.edit_case_id = case_item['id']
                    st.session_state.edit_dialog_open = True
                    st.rerun()
            with col_delete:
                if st.button("Del", key=f"delete_{case_item['id']}", help="Fall löschen", use_container_width=True):
                    delete_case(case_item['id'])
                    st.toast(f"Fall {case_item['case_number']} gelöscht.", icon="✅")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True) # End case item container

st.markdown('</div>', unsafe_allow_html=True) # End Recent Cases Content
st.markdown('</div>', unsafe_allow_html=True) # End Recent Cases Card


# --- Quick Links Section ---
st.markdown('<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">', unsafe_allow_html=True)

col_links_1, col_links_2 = st.columns(2)

with col_links_1:
    st.markdown("""
        <a href="Laborparameter" target="_self" style="text-decoration: none;">
            <div class="link-card-blue">
                <h3 style="font-size: 1.25rem; font-weight: 700; color: white; margin-bottom: 0.5rem; margin-top: 0;">Laborparameter verwalten</h3>
                <p style="color: #BFDBFE;">Übersicht aller verfügbaren Labortests und deren Eigenschaften</p>
            </div>
        </a>
    """, unsafe_allow_html=True)

with col_links_2:
    st.markdown("""
        <a href="Empfehlungen" target="_self" style="text-decoration: none;">
            <div class="link-card-green">
                <h3 style="font-size: 1.25rem; font-weight: 700; color: white; margin-bottom: 0.5rem; margin-top: 0;">Empfehlungen konfigurieren</h3>
                <p style="color: #D1FAE5;">Regelwerk für diagnostikbasierte Laborempfehlungen pflegen</p>
            </div>
        </a>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # End Quick Links Grid
st.markdown('</div>', unsafe_allow_html=True) # Main Container End


# --- Edit Dialog (Simulated Modal) ---
# ACHTUNG: Das Edit-Dialog hier ist vereinfacht und bearbeitet nur grundlegende Felder.
# Eine vollständige Bearbeitung der neuen Felder (Patientennummer, Alter, etc.) wäre 
# ein umfangreiches Feature, das dem "Neuer Fall"-Prozess ähneln würde.
if st.session_state.get('edit_dialog_open', False) and st.session_state.get('edit_case_id'):
    case_id = st.session_state.edit_case_id
    current_case = next((c for c in cases if c['id'] == case_id), None)

    if current_case:
        with st.form(key="edit_case_form"):
            st.markdown("### Fall bearbeiten")

            default_tests_string = ", ".join(current_case.get('ordered_tests', []))

            col_diag1, col_diag2 = st.columns(2)
            with col_diag1:
                st.text_input("Fallnummer", value=current_case.get('case_number', ''), key="edit_case_number_display", disabled=True)
            with col_diag2:
                edited_mts_category = st.selectbox("MTS-Kategorie", options=MTS_CATEGORIES, index=MTS_CATEGORIES.index(current_case.get('mts_category', 'Blau')), key="edit_mts_category")
            
            edited_patient_number = st.text_input("Patientennummer", value=current_case.get('patient_number', ''), key="edit_patient_number")
            edited_suspected_diagnosis = st.text_input("Verdachtsdiagnose", value=current_case.get('suspected_diagnosis', ''), key="edit_suspected_diagnosis")
            
            all_lab_test_codes = [t['test_code'] for t in lab_tests]
            edited_ordered_tests_string = st.text_input(
                "Angeforderte Tests (kommagetrennt)",
                value=default_tests_string,
                help=f"Verfügbar: {', '.join(all_lab_test_codes)}",
                key="edit_ordered_tests_string"
            )

            col_dialog_buttons_1, col_dialog_buttons_2 = st.columns(2)
            with col_dialog_buttons_1:
                if st.form_submit_button("Speichern", type="primary"):
                    updated_ordered_tests = [t.strip() for t in edited_ordered_tests_string.split(',') if t.strip()]
                    updated_data = {
                        "mts_category": edited_mts_category,
                        "patient_number": edited_patient_number,
                        "suspected_diagnosis": edited_suspected_diagnosis,
                        "ordered_tests": updated_ordered_tests,
                    }
                    update_case(case_id, updated_data)
                    st.session_state.edit_dialog_open = False
                    st.toast(f"Fall {current_case['case_number']} aktualisiert.", icon="👍")
                    st.rerun()
            with col_dialog_buttons_2:
                if st.form_submit_button("Abbrechen"):
                    st.session_state.edit_dialog_open = False
                    st.rerun()

    if st.session_state.edit_dialog_open:
        st.info("Hinweis: Nicht alle Felder können hier bearbeitet werden. Nur grundlegende Falldaten.", icon="⚠️")