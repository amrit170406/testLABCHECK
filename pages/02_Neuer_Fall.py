# pages/02_Neuer_Fall.py

import streamlit as st
from utils import init_state, custom_css, MTS_CATEGORIES, MTS_COLOR_MAP, create_case
import time

# ---------------------- Setup ----------------------
st.set_page_config(layout="wide", page_title="Neuer Fall")
init_state()  # Session State initialisieren
custom_css()  # Dark Theme + Modern UI CSS

# ---------------------- Daten aus Session State ----------------------
_lab_tests = st.session_state.lab_tests
_recommendations = st.session_state.recommendations
_diagnoses = st.session_state.diagnoses

# ---------------------- Step Management ----------------------
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'new_case_data' not in st.session_state:
    st.session_state.new_case_data = {}
if 'selected_tests' not in st.session_state:
    st.session_state.selected_tests = []
if 'current_recommendation' not in st.session_state:
    st.session_state.current_recommendation = None
if 'is_analyzing' not in st.session_state:
    st.session_state.is_analyzing = False

def next_step(data={}):
    st.session_state.new_case_data.update(data)
    st.session_state.step += 1

def prev_step():
    if st.session_state.step > 0:
        st.session_state.step -= 1

def handle_analyze():
    mts = st.session_state.new_case_data.get('mts_category')
    diag = st.session_state.new_case_data.get('suspected_diagnosis', '').strip()
    
    if not diag:
        st.error("Bitte Verdachtsdiagnose eingeben.")
        return

    st.session_state.is_analyzing = True
    time.sleep(0.8)  # Simulate network delay
    
    matching_rec = next((
        r for r in _recommendations
        if r['diagnosis_name'].lower() == diag.lower() and r['mts_category'] == mts
    ), None)

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
            "rationale": "Keine spezifische Empfehlung gefunden. Bitte manuelle Auswahl."
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
        "recommended_tests": rec['recommended_tests'] if rec else [],
        "mandatory_tests_rec": rec['mandatory_tests'] if rec else [],
        "optional_tests_rec": rec['optional_tests'] if rec else [],
        "missing_tests": missing_tests,
        "unnecessary_tests": unnecessary_tests,
        "estimated_total_duration": max_duration,
    }

    create_case(case_data)
    st.toast("Neuer Fall erfolgreich gespeichert!", icon="✅")

    st.session_state.step = 0
    st.session_state.new_case_data = {}
    st.session_state.selected_tests = []
    st.session_state.current_recommendation = None
    st.experimental_rerun()

# ---------------------- Navigation Button ----------------------
def nav_button(label, page):
    st.markdown(f"""
        <a href="/{page}" style="text-decoration:none;">
            <div class="modern-button">{label}</div>
        </a>
    """, unsafe_allow_html=True)

# ---------------------- UI Layout ----------------------
st.markdown('<div class="max-w-4xl mx-auto py-6">', unsafe_allow_html=True)
nav_button("Zurück zum Dashboard", "app")

st.markdown("<h1 style='font-size: 2.25rem; font-weight: 700; color: #E2E8F0;'>Neuer Fall anlegen</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94A3B8;'>Patientendaten erfassen & Laborempfehlungen abrufen</p>", unsafe_allow_html=True)
st.markdown("---")

MAX_STEPS = 6
st.progress((st.session_state.step + 1)/MAX_STEPS, text=f"Schritt {st.session_state.step+1}/{MAX_STEPS}")
st.markdown("<br>", unsafe_allow_html=True)

# ---------------------- STEP 0: Patientendaten ----------------------
if st.session_state.step == 0:
    with st.form("step_0_form"):
        st.markdown("### 1. Patientendaten")
        patient_number = st.text_input("Patientennummer", value=st.session_state.new_case_data.get('patient_number', ''))
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Alter", min_value=0, max_value=120, value=st.session_state.new_case_data.get('age', 35))
        with col2:
            gender = st.selectbox("Geschlecht", ["Männlich","Weiblich","Divers"], index=["Männlich","Weiblich","Divers"].index(st.session_state.new_case_data.get('gender', "Männlich")))

        col_back, col_next = st.columns(2)
        with col_back:
            if st.form_submit_button("Zurück"):
                prev_step()
                st.experimental_rerun()
        with col_next:
            if st.form_submit_button("Weiter"):
                if patient_number.strip() == "":
                    st.error("Bitte Patientennummer eingeben")
                else:
                    next_step({"patient_number": patient_number, "age": age, "gender": gender})
                    st.experimental_rerun()

# ---------------------- STEP 1: MTS ----------------------
elif st.session_state.step == 1:
    with st.form("step_1_form"):
        st.markdown("### 2. Dringlichkeit (MTS)")
        mts = st.selectbox("MTS-Kategorie wählen", MTS_CATEGORIES, index=MTS_CATEGORIES.index(st.session_state.new_case_data.get('mts_category','Gelb')))
        col_back, col_next = st.columns(2)
        with col_back:
            if st.form_submit_button("Zurück"):
                prev_step()
                st.experimental_rerun()
        with col_next:
            if st.form_submit_button("Weiter"):
                next_step({"mts_category": mts})
                st.experimental_rerun()

# ---------------------- STEP 2: Symptome ----------------------
elif st.session_state.step == 2:
    with st.form("step_2_form"):
        st.markdown("### 3. Symptome / Anamnese")
        symptoms = st.text_area("Hauptsymptome", height=150, value=st.session_state.new_case_data.get('symptoms',''))
        col_back, col_next = st.columns(2)
        with col_back:
            if st.form_submit_button("Zurück"):
                prev_step()
                st.experimental_rerun()
        with col_next:
            if st.form_submit_button("Weiter"):
                next_step({"symptoms": symptoms})
                st.experimental_rerun()

# ---------------------- STEP 3: Vitalparameter ----------------------
elif st.session_state.step == 3:
    vitals = st.session_state.new_case_data.get('vitals', {})
    with st.form("step_3_form"):
        st.markdown("### 4. Vitalparameter")
        col1, col2 = st.columns(2)
        with col1:
            blood_pressure = st.text_input("Blutdruck", value=vitals.get('blood_pressure',''))
            temperature = st.number_input("Temperatur", 30.0, 42.0, vitals.get('temperature',36.8), step=0.1)
            heart_rate = st.number_input("Herzfrequenz",30,200,vitals.get('heart_rate',75))
        with col2:
            respiratory_rate = st.number_input("Atemfrequenz",5,50,vitals.get('respiratory_rate',16))
            oxygen_saturation = st.number_input("Sauerstoffsättigung",50,100,vitals.get('oxygen_saturation',98))
            blood_sugar = st.number_input("Blutzucker",30,500,vitals.get('blood_sugar',110))
        col_back, col_next = st.columns(2)
        with col_back:
            if st.form_submit_button("Zurück"):
                prev_step()
                st.experimental_rerun()
        with col_next:
            if st.form_submit_button("Weiter"):
                next_step({
                    "vitals": {
                        "blood_pressure": blood_pressure, "temperature": temperature, "heart_rate": heart_rate,
                        "respiratory_rate": respiratory_rate, "oxygen_saturation": oxygen_saturation, "blood_sugar": blood_sugar
                    }
                })
                st.experimental_rerun()

# ---------------------- STEP 4: Diagnose & KI ----------------------
elif st.session_state.step == 4:
    st.markdown("### 5. Verdachtsdiagnose & KI-Analyse")
    diag_input = st.text_input("Verdachtsdiagnose", value=st.session_state.new_case_data.get('suspected_diagnosis',''), placeholder="z.B. Akutes Koronarsyndrom")
    col_back, col_analyze = st.columns(2)
    with col_back:
        if st.button("Zurück"):
            prev_step()
            st.experimental_rerun()
    with col_analyze:
        if st.button("KI-Empfehlung abrufen", disabled=st.session_state.is_analyzing or diag_input.strip()==""):
            st.session_state.new_case_data['suspected_diagnosis'] = diag_input
            handle_analyze()
            st.experimental_rerun()
    if st.session_state.is_analyzing:
        st.info("Analysiere Falldaten...", icon="⏳")

# ---------------------- STEP 5: Testauswahl ----------------------
elif st.session_state.step == 5:
    st.markdown("### 6. Laborwert-Empfehlung")
    rec = st.session_state.current_recommendation
    if rec:
        recommended_codes = set(rec.get('recommended_tests',[]))
        mandatory_codes = set(rec.get('mandatory_tests',[]))
        optional_codes = set(rec.get('optional_tests',[]))
        cols = st.columns(3)
        for i, test in enumerate(_lab_tests):
            with cols[i%3]:
                checked = test['test_code'] in st.session_state.selected_tests
                if st.checkbox(f"{test['test_name']} ({test['test_code']})", value=checked, key=f"sel_{test['test_code']}"):
                    if test['test_code'] not in st.session_state.selected_tests:
                        st.session_state.selected_tests.append(test['test_code'])
                else:
                    if test['test_code'] in st.session_state.selected_tests:
                        st.session_state.selected_tests.remove(test['test_code'])
                st.caption(f"Dauer: {test['estimated_duration_minutes']} min")
        col_back, col_submit = st.columns(2)
        with col_back:
            if st.button("Zurück"):
                prev_step()
                st.experimental_rerun()
        with col_submit:
            if st.button("Fall speichern", disabled=len(st.session_state.selected_tests)==0):
                handle_submit()
                st.experimental_rerun()

# ---------------------- Fallback ----------------------
else:
    st.error("Unerwarteter Fehler. Prozess wird neu gestartet.")
    if st.button("Neu starten"):
        st.session_state.step = 0
        st.session_state.new_case_data = {}
        st.session_state.selected_tests = []
        st.session_state.current_recommendation = None
        st.experimental_rerun()

st.markdown('</div>', unsafe_allow_html=True)
