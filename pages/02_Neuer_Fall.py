# pages/02_Neuer_Fall.py

import streamlit as st
from utils import init_state, custom_css, MTS_CATEGORIES, _MTS_COLOR_MAP, create_case
import time

# --- Setup ---
st.set_page_config(layout="wide", page_title="Neuer Fall")
init_state()
custom_css()

_lab_tests = st.session_state.lab_tests
_recommendations = st.session_state.recommendations

# --- Hilfsfunktionen ---
def next_step(data={}):
    st.session_state.new_case_data.update(data)
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

def handle_analyze():
    """Führt KI-Analyse für Laborwerte aus."""
    mts = st.session_state.new_case_data.get('mts_category')
    diag = st.session_state.new_case_data.get('suspected_diagnosis', '')
    
    st.session_state.is_analyzing = True
    time.sleep(0.8)  # Simuliert Verarbeitung
    
    matching_rec = next(
        (r for r in _recommendations
         if r['diagnosis_name'].lower() == diag.lower() and r['mts_category'] == mts),
        None
    )
    
    if matching_rec:
        st.session_state.current_recommendation = matching_rec
        st.session_state.selected_tests = matching_rec['recommended_tests']
    else:
        st.session_state.current_recommendation = {
            "diagnosis_name": diag,
            "mts_category": mts,
            "recommended_tests": [],
            "mandatory_tests": [],
            "optional_tests": [],
            "rationale": "Keine Empfehlung gefunden. Bitte manuell auswählen."
        }
        st.session_state.selected_tests = []

    st.session_state.is_analyzing = False
    next_step()

def handle_submit():
    rec = st.session_state.current_recommendation
    selected_tests = st.session_state.selected_tests
    
    if not selected_tests:
        st.error("Bitte wählen Sie mindestens einen Test aus.")
        return

    mandatory_tests = rec.get('mandatory_tests', []) if rec else []
    recommended_set = set(rec.get('recommended_tests', [])) if rec else set()
    optional_test_codes = set(rec.get('optional_tests', [])) if rec else set()

    missing_tests = [t for t in mandatory_tests if t not in selected_tests]
    unnecessary_tests = [t for t in selected_tests if t not in recommended_set and t not in optional_test_codes]

    max_duration = max([t['estimated_duration_minutes'] for t in _lab_tests if t['test_code'] in selected_tests], default=0)

    case_data = {
        **st.session_state.new_case_data,
        "ordered_tests": selected_tests,
        "recommended_tests": rec.get('recommended_tests', []),
        "mandatory_tests_rec": rec.get('mandatory_tests', []),
        "optional_tests_rec": rec.get('optional_tests', []),
        "missing_tests": missing_tests,
        "unnecessary_tests": unnecessary_tests,
        "estimated_total_duration": max_duration
    }

    create_case(case_data)
    st.toast("Neuer Fall erfolgreich gespeichert!", icon="✅")

    st.session_state.step = 0
    st.session_state.new_case_data = {}
    st.session_state.selected_tests = []
    st.session_state.current_recommendation = None
    st.switch_page("app.py")

# --- UI Layout ---
st.markdown('<div class="max-w-4xl mx-auto py-6">', unsafe_allow_html=True)
st.page_link("app.py", label="Zurück zum Dashboard", icon="home")
st.markdown("<h1 style='font-size:2.25rem; font-weight:700;color:#0F172A;'>Neuer Fall anlegen</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B;'>Erfassen Sie Patientendaten und Laborempfehlungen</p>", unsafe_allow_html=True)
st.markdown("---")

MAX_STEPS = 6
st.progress((st.session_state.step + 1) / MAX_STEPS, text=f"Schritt {st.session_state.step+1}/{MAX_STEPS}")
st.markdown("<br>", unsafe_allow_html=True)

# ----------------- STEP 0: Identifikation -----------------
if st.session_state.step == 0:
    with st.form("step_0_form", clear_on_submit=False):
        st.markdown("### 1. Patientendaten")
        patient_number = st.text_input("Patientennummer", placeholder="Patienten-ID eingeben",
                                       value=st.session_state.new_case_data.get('patient_number',''))
        col_age, col_gender = st.columns(2)
        with col_age:
            age = st.number_input("Alter (Jahre)", min_value=0, max_value=120,
                                  value=st.session_state.new_case_data.get('age',35))
        with col_gender:
            gender_options = ["Männlich","Weiblich","Divers"]
            gender = st.selectbox("Geschlecht", gender_options,
                                  index=gender_options.index(st.session_state.new_case_data.get('gender',gender_options[0])))
        if st.form_submit_button("Weiter zu MTS-Einstufung"):
            if patient_number:
                next_step({"patient_number": patient_number, "age": age, "gender": gender})
                st.rerun()
            else:
                st.error("Bitte Patientennummer eingeben.")

# ----------------- STEP 1: MTS -----------------
elif st.session_state.step == 1:
    with st.form("step_1_form"):
        st.markdown("### 2. Dringlichkeit (MTS-Einstufung)")
        mts_category = st.selectbox("MTS-Kategorie", MTS_CATEGORIES,
                                    index=MTS_CATEGORIES.index(st.session_state.new_case_data.get('mts_category','Gelb')))
        st.info("Das Manchester-Triage-System (MTS) dient zur Ersteinschätzung.", icon="ℹ️")
        col_back, col_next = st.columns(2)
        with col_back:
            st.form_submit_button("Zurück", on_click=prev_step)
        with col_next:
            if st.form_submit_button("Weiter zu Symptome"):
                next_step({"mts_category": mts_category})
                st.rerun()

# ----------------- STEP 2: Symptome -----------------
elif st.session_state.step == 2:
    with st.form("step_2_form"):
        st.markdown("### 3. Klinisches Bild (Symptome)")
        symptoms = st.text_area("Hauptsymptome", placeholder="z.B. Brustschmerz, Übelkeit...", height=150,
                                value=st.session_state.new_case_data.get('symptoms',''))
        col_back, col_next = st.columns(2)
        with col_back:
            st.form_submit_button("Zurück", on_click=prev_step)
        with col_next:
            if st.form_submit_button("Weiter zu Vitalparameter"):
                next_step({"symptoms": symptoms})
                st.rerun()

# ----------------- STEP 3: Vitalparameter -----------------
elif st.session_state.step == 3:
    vitals = st.session_state.new_case_data.get('vitals', {})
    with st.form("step_3_form"):
        st.markdown("### 4. Vitalparameter")
        col1, col2 = st.columns(2)
        with col1:
            blood_pressure = st.text_input("Blutdruck", value=vitals.get('blood_pressure',''))
            temperature = st.number_input("Temperatur (°C)", 30.0, 42.0, vitals.get('temperature',36.8), step=0.1)
            heart_rate = st.number_input("Herzfrequenz (bpm)", 30, 200, vitals.get('heart_rate',75))
        with col2:
            respiratory_rate = st.number_input("Atemfrequenz",5,50,vitals.get('respiratory_rate',16))
            oxygen_saturation = st.number_input("Sauerstoff (%)",50,100,vitals.get('oxygen_saturation',98))
            blood_sugar = st.number_input("Blutzucker",30,500,vitals.get('blood_sugar',110))
        col_back, col_next = st.columns(2)
        with col_back:
            st.form_submit_button("Zurück", on_click=prev_step)
        with col_next:
            if st.form_submit_button("Weiter zu Diagnose"):
                next_step({"vitals": {"blood_pressure": blood_pressure, "temperature": temperature,
                                       "heart_rate": heart_rate, "respiratory_rate": respiratory_rate,
                                       "oxygen_saturation": oxygen_saturation, "blood_sugar": blood_sugar}})
                st.rerun()

# ----------------- STEP 4: Diagnose -----------------
elif st.session_state.step == 4:
    st.markdown("### 5. Verdachtsdiagnose & KI-Analyse")
    st.text_input("Verdachtsdiagnose", key="current_diagnosis_input",
                  value=st.session_state.new_case_data.get('suspected_diagnosis',''),
                  help=f"Verfügbar: {', '.join([d['diagnosis_name'] for d in _recommendations])}")
    col_back, col_analyze = st.columns(2)
    with col_back:
        st.button("Zurück zu Vitalparameter", on_click=prev_step)
    with col_analyze:
        if st.button("KI-Empfehlung abrufen", disabled=st.session_state.is_analyzing or not st.session_state.current_diagnosis_input):
            st.session_state.new_case_data['suspected_diagnosis'] = st.session_state.current_diagnosis_input
            handle_analyze()
            st.rerun()
    if st.session_state.is_analyzing:
        st.info("Analysiere Daten...", icon="⏳")

# ----------------- STEP 5: Testauswahl -----------------
elif st.session_state.step == 5:
    st.markdown("### 6. Laborwert-Empfehlung & Auswahl")
    rec = st.session_state.current_recommendation
    if rec:
        recommended_codes = set(rec.get('recommended_tests',[]))
        mandatory_codes = set(rec.get('mandatory_tests',[]))
        optional_codes = set(rec.get('optional_tests',[]))
        
        st.markdown('<div class="stCard-custom">', unsafe_allow_html=True)
        st.markdown('<div class="stCard-header">Empfohlene Tests</div>', unsafe_allow_html=True)
        if rec.get('rationale'):
            st.markdown(f'<div class="alert-blue">{rec["rationale"]}</div>', unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, test in enumerate([t for t in _lab_tests if t['test_code'] in recommended_codes]):
            with cols[i % 3]:
                checked = test['test_code'] in st.session_state.selected_tests
                if st.checkbox(f"{test['test_name']} ({test['test_code']})", value=checked, key=f"rec_test_{test['test_code']}"):
                    if test['test_code'] not in st.session_state.selected_tests:
                        st.session_state.selected_tests.append(test['test_code'])
                else:
                    if test['test_code'] in st.session_state.selected_tests:
                        st.session_state.selected_tests.remove(test['test_code'])
                if test['test_code'] in mandatory_codes:
                    st.markdown('<span class="badge-destructive">Pflicht</span>', unsafe_allow_html=True)
                st.caption(f"Dauer: {test['estimated_duration_minutes']} min")
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_back, col_submit = st.columns(2)
        with col_back:
            st.button("Zurück zur Diagnose", on_click=prev_step)
        with col_submit:
            st.button("Fall speichern", on_click=handle_submit, disabled=len(st.session_state.selected_tests)==0, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
