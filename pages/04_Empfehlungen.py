# pages/04_Empfehlungen.py

import streamlit as st
from utils import init_state, custom_css, MTS_CATEGORIES, MTS_COLOR_MAP, create_recommendation, delete_recommendation, lab_tests
import time

st.set_page_config(layout="wide", page_title="Laborempfehlungen")
init_state()
custom_css()

# --- Datenabruf ---
recommendations = st.session_state.recommendations
test_codes = [t['test_code'] for t in lab_tests] # Holen Sie sich die tatsächlichen Test-Codes

# --- UI Layout ---
st.markdown('<div class="max-w-7xl mx-auto py-6">', unsafe_allow_html=True) # Main Container

st.page_link("app.py", label="Zurück zum Dashboard", icon="arrow_left")

col_header_1, col_header_2 = st.columns([3, 1])

with col_header_1:
    st.markdown("<h1 style='font-size: 2.25rem; font-weight: 700; color: #0F172A;'>Laborempfehlungen</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Regelwerk für diagnostikbasierte Empfehlungen</p>", unsafe_allow_html=True)

with col_header_2:
    if st.button("Neue Regel anlegen", key="new_rec_button", use_container_width=True, type="primary"):
        st.session_state.new_rec_dialog_open = True

# --- New Recommendation Dialog (Form) ---
if st.session_state.get('new_rec_dialog_open', False):
    with st.form(key="new_rec_form"):
        st.markdown("### Neue Empfehlungsregel anlegen")

        col_diag1, col_diag2 = st.columns(2)
        with col_diag1:
            new_diagnosis_name = st.text_input("Verdachtsdiagnose", placeholder="z.B. Akutes Koronarsyndrom")
        with col_diag2:
            new_mts_category = st.selectbox("MTS-Kategorie", options=MTS_CATEGORIES, index=2)
        
        st.markdown("---")
        
        # Multi-select für Tests (professioneller als Text-Input)
        new_recommended_tests_sel = st.multiselect(
            "Empfohlene Tests",
            options=test_codes,
            help="Tests, die basierend auf Diagnose und Dringlichkeit vorgeschlagen werden."
        )
        new_mandatory_tests_sel = st.multiselect(
            "Pflicht-Tests",
            options=test_codes,
            help="Tests, deren Fehlen als Warnung angezeigt wird."
        )
        new_optional_tests_sel = st.multiselect(
            "Optionale Tests",
            options=test_codes,
            help="Tests, die nicht empfohlen, aber für diese Diagnose relevant sein können."
        )
        
        new_rationale = st.text_area("Begründung", placeholder="Klinische Begründung für diese Empfehlung...", height=100)

        col_dialog_buttons_1, col_dialog_buttons_2 = st.columns(2)
        with col_dialog_buttons_1:
            if st.form_submit_button("Speichern", type="primary"):
                if not new_diagnosis_name or not new_recommended_tests_sel:
                    st.error("Diagnose und Empfohlene Tests sind Pflichtfelder.")
                else:
                    data = {
                        "diagnosis_name": new_diagnosis_name,
                        "mts_category": new_mts_category,
                        "recommended_tests": new_recommended_tests_sel,
                        "mandatory_tests": new_mandatory_tests_sel,
                        "optional_tests": new_optional_tests_sel,
                        "rationale": new_rationale
                    }
                    create_recommendation(data)
                    st.session_state.new_rec_dialog_open = False
                    st.toast(f"Regel für '{new_diagnosis_name}' angelegt.", icon="👍")
                    st.rerun()
        with col_dialog_buttons_2:
            if st.form_submit_button("Abbrechen"):
                st.session_state.new_rec_dialog_open = False
                st.rerun()

# --- Recommendations Display ---
st.markdown('<div class="stCard-custom">', unsafe_allow_html=True)
st.markdown('<div class="stCard-content">', unsafe_allow_html=True)

if not recommendations:
    st.markdown("""
        <div style="text-align: center; padding: 3rem 0;">
            <p style="color: #64748B; margin-bottom: 1rem;">Noch keine Empfehlungsregeln angelegt</p>
            <div class="green-button">
                {st.button("Erste Regel anlegen", key="first_rec_button", type="primary")}
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.session_state.get("first_rec_button"):
        st.session_state.new_rec_dialog_open = True
        st.rerun()
else:
    for rec in recommendations:
        mts_style = MTS_COLOR_MAP.get(rec['mts_category'], 'background-color: #94A3B8;')
        
        st.markdown(f"""
            <div style="border: 1px solid #E2E8F0; border-radius: 0.75rem; padding: 1rem; margin-bottom: 1rem; background-color: white;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <div style="width: 16px; height: 16px; border-radius: 9999px; {mts_style}"></div>
                        <div>
                            <h4 style="font-size: 1.125rem; font-weight: 600; color: #0F172A; margin: 0;">{rec['diagnosis_name']}</h4>
                            <span class="badge-base badge-outline" style="margin-top: 0.25rem;">{rec['mts_category']}</span>
                        </div>
                    </div>
                    <div class="red-button">
                        {st.button('🗑️', key=f"delete_rec_{rec['id']}", help="Regel löschen")}
                    </div>
                </div>
                
                {rec.get('rationale') and f'<p style="font-size: 0.875rem; color: #475569; font-style: italic; margin-bottom: 1rem;">{rec["rationale"]}</p>'}

                <div style="margin-bottom: 0.75rem;">
                    <p style="font-size: 0.75rem; font-weight: 600; color: #475569; margin-bottom: 0.25rem;">Empfohlene Tests:</p>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        {''.join([f'<span class="badge-base badge-blue">{t}</span>' for t in rec.get('recommended_tests', [])])}
                    </div>
                </div>

                {rec.get('mandatory_tests') and len(rec['mandatory_tests']) > 0 and 
                    f"""
                    <div style="margin-bottom: 0.75rem;">
                        <p style="font-size: 0.75rem; font-weight: 600; color: #475569; margin-bottom: 0.25rem;">Pflicht-Tests:</p>
                        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                            {''.join([f'<span class="badge-base badge-destructive">{t}</span>' for t in rec['mandatory_tests']])}
                        </div>
                    </div>
                    """}

                {rec.get('optional_tests') and len(rec['optional_tests']) > 0 and 
                    f"""
                    <div>
                        <p style="font-size: 0.75rem; font-weight: 600; color: #475569; margin-bottom: 0.25rem;">Optional:</p>
                        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                            {''.join([f'<span class="badge-base badge-outline">{t}</span>' for t in rec['optional_tests']])}
                        </div>
                    </div>
                    """}
            </div>
        """, unsafe_allow_html=True)

        # Handle Delete Action
        if st.session_state.get(f"delete_rec_{rec['id']}"):
            delete_recommendation(rec['id'])
            st.toast(f"Regel für '{rec['diagnosis_name']}' gelöscht.", icon="❌")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)