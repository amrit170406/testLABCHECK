# pages/04_Empfehlungen.py

import streamlit as st
from utils import init_state, custom_css, MTS_CATEGORIES, MTS_COLOR_MAP, create_recommendation, delete_recommendation, LAB_CATEGORIES_BADGE_MAP

# --- Setup ---
st.set_page_config(layout="wide", page_title="Laborempfehlungen")
init_state()
custom_css()

_recommendations = st.session_state.recommendations
_lab_tests = st.session_state.lab_tests

# --- Helper: Test-Codes für Multi-Select ---
test_codes = [t['test_code'] for t in _lab_tests]

# --- Main Container ---
st.markdown('<div class="max-w-7xl mx-auto py-6">', unsafe_allow_html=True)
st.page_link("app.py", label="Zurück zum Dashboard", icon="home")

# Header
col1, col2 = st.columns([3,1])
with col1:
    st.markdown("<h1 style='font-size:2.25rem;font-weight:700;color:#0F172A;'>Laborempfehlungen</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B;'>Regelwerk für diagnostikbasierte Empfehlungen</p>", unsafe_allow_html=True)
with col2:
    if st.button("Neue Regel anlegen", key="new_rec_button", use_container_width=True, type="primary"):
        st.session_state.new_rec_dialog_open = True

# --- New Recommendation Dialog ---
if st.session_state.get('new_rec_dialog_open', False):
    with st.form("new_rec_form"):
        st.markdown("### Neue Empfehlungsregel anlegen")

        col_diag1, col_diag2 = st.columns(2)
        with col_diag1:
            new_diag_name = st.text_input("Verdachtsdiagnose", placeholder="z.B. Akutes Koronarsyndrom")
        with col_diag2:
            new_mts_category = st.selectbox("MTS-Kategorie", options=MTS_CATEGORIES, index=2)
        
        st.markdown("---")
        new_recommended_tests = st.multiselect("Empfohlene Tests", options=test_codes, help="Tests, die basierend auf Diagnose & Dringlichkeit vorgeschlagen werden.")
        new_mandatory_tests = st.multiselect("Pflicht-Tests", options=test_codes, help="Müssen Teil der empfohlenen Tests sein.")
        new_optional_tests = st.multiselect("Optionale Tests", options=test_codes, help="Tests, die optional relevant sein können.")
        new_rationale = st.text_area("Begründung", placeholder="Klinische Begründung für diese Empfehlung...", height=100)

        col_save, col_cancel = st.columns(2)
        with col_save:
            if st.form_submit_button("Speichern", type="primary"):
                # Validierung
                if not new_diag_name or not new_recommended_tests:
                    st.error("Diagnose und empfohlene Tests sind Pflichtfelder.")
                elif not set(new_mandatory_tests).issubset(set(new_recommended_tests)):
                    st.error("Pflicht-Tests müssen Teil der empfohlenen Tests sein.")
                else:
                    create_recommendation({
                        "diagnosis_name": new_diag_name,
                        "mts_category": new_mts_category,
                        "recommended_tests": new_recommended_tests,
                        "mandatory_tests": new_mandatory_tests,
                        "optional_tests": new_optional_tests,
                        "rationale": new_rationale
                    })
                    st.session_state.new_rec_dialog_open = False
                    st.toast(f"Regel für '{new_diag_name}' angelegt.", icon="👍")
                    st.rerun()
        with col_cancel:
            if st.form_submit_button("Abbrechen"):
                st.session_state.new_rec_dialog_open = False
                st.rerun()

# --- Display Recommendations ---
st.markdown('<div class="stCard-custom">', unsafe_allow_html=True)
st.markdown('<div class="stCard-content">', unsafe_allow_html=True)

if not _recommendations:
    st.markdown("""
        <div style="text-align:center;padding:3rem 0;">
            <p style="color:#64748B;">Noch keine Empfehlungsregeln angelegt</p>
        </div>
    """, unsafe_allow_html=True)
else:
    for rec in _recommendations:
        mts_style = MTS_COLOR_MAP.get(rec['mts_category'], 'background-color:#94A3B8;')
        st.markdown(f"""
            <div style="border:1px solid #E2E8F0;border-radius:0.75rem;padding:1rem;margin-bottom:1rem;background:white;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.75rem;">
                    <div style="display:flex;align-items:center;gap:0.75rem;">
                        <div class="mts-dot" style="{mts_style}"></div>
                        <div>
                            <h4 style="font-size:1.125rem;font-weight:600;color:#0F172A;margin:0;">{rec['diagnosis_name']}</h4>
                            <span class="badge-base badge-outline" style="margin-top:0.25rem;">{rec['mts_category']}</span>
                        </div>
                    </div>
                    <div class="red-button">{st.button('🗑️', key=f"delete_rec_{rec['id']}", help="Regel löschen")}</div>
                </div>

                {f'<p style="font-size:0.875rem;color:#475569;font-style:italic;margin-bottom:1rem;">{rec["rationale"]}</p>' if rec.get('rationale') else ''}

                <div style="margin-bottom:0.75rem;">
                    <p style="font-size:0.75rem;font-weight:600;color:#475569;margin-bottom:0.25rem;">Empfohlene Tests:</p>
                    <div style="display:flex;flex-wrap:wrap;gap:0.5rem;">
                        {''.join([f'<span class="badge-base badge-blue">{t}</span>' for t in rec.get('recommended_tests', [])])}
                    </div>
                </div>

                {rec.get('mandatory_tests') and len(rec['mandatory_tests'])>0 and f"""
                    <div style="margin-bottom:0.75rem;">
                        <p style="font-size:0.75rem;font-weight:600;color:#475569;margin-bottom:0.25rem;">Pflicht-Tests:</p>
                        <div style="display:flex;flex-wrap:wrap;gap:0.5rem;">
                            {''.join([f'<span class="badge-base badge-destructive">{t}</span>' for t in rec['mandatory_tests']])}
                        </div>
                    </div>
                """}

                {rec.get('optional_tests') and len(rec['optional_tests'])>0 and f"""
                    <div>
                        <p style="font-size:0.75rem;font-weight:600;color:#475569;margin-bottom:0.25rem;">Optional:</p>
                        <div style="display:flex;flex-wrap:wrap;gap:0.5rem;">
                            {''.join([f'<span class="badge-base badge-outline">{t}</span>' for t in rec['optional_tests']])}
                        </div>
                    </div>
                """}
            </div>
        """, unsafe_allow_html=True)

        # Delete action
        if st.session_state.get(f"delete_rec_{rec['id']}"):
            delete_recommendation(rec['id'])
            st.toast(f"Regel für '{rec['diagnosis_name']}' gelöscht.", icon="❌")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
