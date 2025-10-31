# pages/02_Neuer_Fall.py

import streamlit as st
from utils import init_state, custom_css, MTS_CATEGORIES, MTS_COLOR_MAP, create_case
import time

# Setup
st.set_page_config(layout="wide", page_title="Neuer Fall | Erfassung")
init_state() 
custom_css()

# --- Datenabruf (aus Session State) ---
_lab_tests = st.session_state.lab_tests
_recommendations = st.session_state.recommendations
_diagnoses = st.session_state.diagnoses


# --- Funktionen ---

def next_step(data={}):
    """Speichert Daten und geht zum nächsten Schritt."""
    st.session_state.new_case_data.update(data)
    st.session_state.step += 1

def prev_step():
    """Geht zum vorherigen Schritt zurück."""
    st.session_state.step -= 1

def handle_analyze():
    """Führt die Logik der Laborwert-Empfehlung aus."""
    mts = st.session_state.new_case_data.get('mts_category')
    diag = st.session_state.new_case_data.get('suspected_diagnosis')
    
    st.session_state.is_analyzing = True
    time.sleep(0.8) # Simulate network delay
    
    matching_rec = next((
        r for r in _recommendations
        if r['diagnosis_name'].lower() == diag.lower() and 
           r['mts_category'] == mts
    ), None)

    if matching_rec:
        st.session_state.current_recommendation = matching_rec
        st.session_state.selected_tests = matching_rec['recommended_tests'].copy() # Wichtig: Kopie verwenden
    else:
        st.session_state.current_recommendation = {
            "diagnosis_name": diag, "mts_category": mts, "recommended_tests": [],
            "mandatory_tests": [], "optional_tests": [], 
            "rationale": "Keine spezifische Empfehlung für diese Diagnose/MTS-Kategorie gefunden. Manuelle Auswahl erforderlich."
        }
        st.session_state.selected_tests = []
        
    st.session_state.is_analyzing = False
    next_step() # Geht zu Schritt 6 (Testauswahl)


def handle_submit():
    """Speichert den Fall im letzten Schritt."""
    rec = st.session_state.current_recommendation
    selected_tests = st.session_state.selected_tests
    
    if not selected_tests:
        st.error("Bitte wählen Sie mindestens einen Test aus.")
        return

    # Analyse der Qualität
    mandatory_tests = rec.get('mandatory_tests', []) if rec else []
    recommended_set = set(rec.get('recommended_tests', [])) if rec else set()
    optional_test_codes = set(rec.get('optional_tests', [])) if rec else set()

    missing_tests = [t for t in mandatory_tests if t not in selected_tests]
    unnecessary_tests = [t for t in selected_tests if t not in recommended_set and t not in optional_test_codes]
    
    max_duration = max([t['estimated_duration_minutes'] for t in _lab_tests if t['test_code'] in selected_tests], default=0)

    # Datenstruktur erstellen
    case_data = {
        **st.session_state.new_case_data, 
        "ordered_tests": selected_tests,
        "recommended_tests": rec['recommended_tests'] if rec else [],
        "missing_tests": missing_tests,
        "unnecessary_tests": unnecessary_tests,
        "estimated_total_duration": max_duration,
    }

    create_case(case_data)
    st.toast("Neuer Fall erfolgreich gespeichert!", icon="✅")
    
    # Zustand zurücksetzen und zum Dashboard navigieren
    st.session_state.step = 0
    st.session_state.new_case_data = {}
    st.session_state.selected_tests = []
    st.session_state.current_recommendation = None
    st.switch_page("app.py")


# --- UI Layout ---
st.markdown('<div class="max-w-4xl mx-auto py-6">', unsafe_allow_html=True)

st.page_link("app.py", label="Zurück zum Dashboard", icon="arrow-left") # Korrektur: Lucide Icon Name
st.markdown("<h1 style='font-size: 2.25rem; font-weight: 700; color: #0F172A;'>Neuer Fall anlegen</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B;'>Führen Sie die Triage durch, erfassen Sie die Vitalparameter und erhalten Sie eine KI-gestützte Laborempfehlung.</p>", unsafe_allow_html=True)
st.markdown("---")


# --- Progress Bar und Steps ---
MAX_STEPS = 6
st.progress((st.session_state.step + 1) / MAX_STEPS, text=f"**Schritt {st.session_state.step+1}/{MAX_STEPS}** abgeschlossen")
st.markdown("<br>", unsafe_allow_html=True)

# ----------------- STEP 0: Identifikation -----------------
if st.session_state.step == 0:
    with st.form(key="step_0_id_form", clear_on_submit=False):
        st.markdown("### 1. Patientendaten (Identifikation) 🧑‍⚕️")
        
        patient_number = st.text_input("Patientennummer", placeholder="Eindeutige Patienten-ID (obligatorisch)", 
                                       value=st.session_state.new_case_data.get('patient_number', ''))
        
        col_age, col_gender = st.columns(2)
        with col_age:
            age = st.number_input("Alter (Jahre)", min_value=0, max_value=120, 
                                  value=st.session_state.new_case_data.get('age', 35), step=1)
        with col_gender:
            gender_options = ['Männlich', 'Weiblich', 'Divers']
            gender = st.selectbox("Geschlecht", options=gender_options, 
                                  index=gender_options.index(st.session_state.new_case_data.get('gender', gender_options[0])))
        
        if st.form_submit_button("Weiter zu MTS-Einstufung", type="primary"):
            if patient_number:
                next_step({"patient_number": patient_number, "age": age, "gender": gender})
                st.rerun()
            else:
                st.error("Bitte geben Sie eine Patientennummer ein.")

# ----------------- STEP 1: MTS-Einstufung -----------------
elif st.session_state.step == 1:
    with st.form(key="step_1_mts_form", clear_on_submit=False):
        st.markdown("### 2. Dringlichkeit (MTS-Einstufung) 🚨")
        
        mts_category = st.selectbox(
            "Wählen Sie die MTS-Kategorie", 
            options=MTS_CATEGORIES, 
            index=MTS_CATEGORIES.index(st.session_state.new_case_data.get('mts_category', 'Gelb')),
            format_func=lambda x: f"● {x}"
        )
        
        st.markdown(f"""
            <div class="alert-blue" style="font-size: 0.875rem;">
                <p style="margin: 0; font-weight: bold; color: {MTS_COLOR_MAP.get(mts_category, '#3B82F6')};">Ausgewählte Kategorie: {mts_category}</p>
                <p style="margin: 0; margin-top: 0.5rem; color: #1D4ED8;">Das Manchester-Triage-System (MTS) bewertet die Behandlungsdringlichkeit.</p>
            </div>
        """, unsafe_allow_html=True)

        col_back, col_next = st.columns(2)
        with col_back:
            st.form_submit_button("Zurück", on_click=prev_step)
        with col_next:
            if st.form_submit_button("Weiter zu Symptomeingabe", type="primary"):
                next_step({"mts_category": mts_category})
                st.rerun()

# ----------------- STEP 2: Symptome -----------------
elif st.session_state.step == 2:
    with st.form(key="step_2_symptoms_form", clear_on_submit=False):
        st.markdown("### 3. Klinisches Bild (Symptome) 🤒")
        
        symptoms = st.text_area("Hauptsymptome und Anamnese", 
                                placeholder="Brustschmerz seit 2 Stunden, Übelkeit, keine Vorerkrankungen bekannt...", 
                                height=150, value=st.session_state.new_case_data.get('symptoms', ''))
        
        col_back, col_next = st.columns(2)
        with col_back:
            st.form_submit_button("Zurück", on_click=prev_step)
        with col_next:
            if st.form_submit_button("Weiter zu Vitalparametern", type="primary"):
                next_step({"symptoms": symptoms})
                st.rerun()

# ----------------- STEP 3: Vitalparameter -----------------
elif st.session_state.step == 3:
    vitals = st.session_state.new_case_data.get('vitals', {})
    
    with st.form(key="step_3_vitals_form", clear_on_submit=False):
        st.markdown("### 4. Vitalparameter 🩸")
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            blood_pressure = st.text_input("Blutdruck (mmHG)", placeholder="z.B. 130/85", value=vitals.get('blood_pressure', ''))
            temperature = st.number_input("Temperatur (°C)", min_value=30.0, max_value=42.0, value=vitals.get('temperature', 36.8), step=0.1, format="%.1f")
            heart_rate = st.number_input("Herzfrequenz (bpm)", min_value=30, max_value=200, value=vitals.get('heart_rate', 75), step=1)
        
        with col_v2:
            respiratory_rate = st.number_input("Atemfrequenz (/min)", min_value=5, max_value=50, value=vitals.get('respiratory_rate', 16), step=1)
            oxygen_saturation = st.number_input("Sauerstoffsättigung (%)", min_value=50, max_value=100, value=vitals.get('oxygen_saturation', 98), step=1)
            blood_sugar = st.number_input("Blutzucker (mg/dl)", min_value=30, max_value=500, value=vitals.get('blood_sugar', 110), step=1)

        col_back, col_next = st.columns(2)
        with col_back:
            st.form_submit_button("Zurück", on_click=prev_step)
        with col_next:
            if st.form_submit_button("Weiter zu Diagnose/Analyse", type="primary"):
                next_step({
                    "vitals": {
                        "blood_pressure": blood_pressure, "temperature": temperature, "heart_rate": heart_rate,
                        "respiratory_rate": respiratory_rate, "oxygen_saturation": oxygen_saturation, "blood_sugar": blood_sugar
                    }
                })
                st.rerun()

# ----------------- STEP 4: Diagnose und KI-Analyse -----------------
elif st.session_state.step == 4:
    diagnosis_input_value = st.session_state.new_case_data.get('suspected_diagnosis', '')
    
    st.markdown("### 5. Verdachtsdiagnose & KI-Analyse 🧠")
    
    available_diagnoses_names = [d['diagnosis_name'] for d in _diagnoses]

    st.text_input(
        "Verdachtsdiagnose",
        placeholder="z.B. Akutes Koronarsyndrom (zur Empfehlungsgenerierung)",
        key='current_diagnosis_input',
        value=diagnosis_input_value,
        help=f"Verfügbar für Empfehlungen (Demo): {', '.join(available_diagnoses_names)}"
    )

    col_back, col_analyze = st.columns(2)
    with col_back:
        st.button("Zurück zu Vitalparametern", on_click=prev_step)
    with col_analyze:
        if st.button("KI-Empfehlung abrufen", type="primary", use_container_width=True, disabled=st.session_state.is_analyzing or not st.session_state.current_diagnosis_input):
            st.session_state.new_case_data['suspected_diagnosis'] = st.session_state.current_diagnosis_input 
            handle_analyze()
            st.rerun()

    if st.session_state.is_analyzing:
        st.info("Analysiere Falldaten und rufe KI-Empfehlung ab...", icon="⏳")

# ----------------- STEP 5: Testauswahl (KI-Ergebnis) -----------------
elif st.session_state.step == 5:
    st.markdown("### 6. Laborwert-Empfehlung und Auswahl ✅")
    
    recommendation = st.session_state.get('current_recommendation')

    if recommendation:
        # --- Empfohlene Laborparameter ---
        st.markdown('<div class="stCard-custom">', unsafe_allow_html=True)
        st.markdown('<div class="stCard-header">Empfohlene Laborparameter (KI-Basis)</div>', unsafe_allow_html=True)
        
        with st.container(border=False):
            if recommendation.get('rationale'):
                st.markdown(f'<div class="alert-blue"><p style="margin: 0; font-size: 0.95rem;">{recommendation["rationale"]}</p></div>', unsafe_allow_html=True)
            
            recommended_test_codes = set(recommendation.get('recommended_tests', []))
            mandatory_test_codes = set(recommendation.get('mandatory_tests', []))
            
            # --- Testauswahl (Multiselect für bessere Usability) ---
            all_lab_test_codes = [t['test_code'] for t in _lab_tests]
            
            # Gruppierung der empfohlenen Tests
            default_selection = [t for t in all_lab_test_codes if t in st.session_state.selected_tests]
            
            selected_tests_multiselect = st.multiselect(
                "Wählen Sie die Labortests aus, die angefordert werden sollen (KI-Vorauswahl)",
                options=all_lab_test_codes,
                default=default_selection,
                help="Die KI-Empfehlungen sind bereits vorausgewählt. Passen Sie die Auswahl manuell an.",
                key="final_test_selection_multiselect"
            )
            # Synchronisiere Multiselect mit Session State
            st.session_state.selected_tests = selected_tests_multiselect
            
            # --- Anzeige der Qualitätsprüfung (dynamisch) ---
            if st.session_state.selected_tests:
                st.markdown("---")
                st.markdown("#### **Qualitätsprüfung** (Live-Analyse)")
                
                selected_tests = st.session_state.selected_tests
                
                missing_tests = [t for t in mandatory_test_codes if t not in selected_tests]
                recommended_set = set(recommendation.get('recommended_tests', []))
                optional_test_codes = set(recommendation.get('optional_tests', []))
                unnecessary_tests = [t for t in selected_tests if t not in recommended_set and t not in optional_test_codes]
                
                if missing_tests:
                    st.markdown(f"""<div class="alert-red"><p style="margin:0;"><span style="font-weight: 600;">Fehlende Pflicht-Tests:</span> {', '.join(missing_tests)}</p></div>""", unsafe_allow_html=True)
                if unnecessary_tests:
                    st.markdown(f"""<div class="alert-amber"><p style="margin:0;"><span style="font-weight: 600;">Möglicherweise überflüssig:</span> {', '.join(unnecessary_tests)}</p></div>""", unsafe_allow_html=True)
                if not missing_tests and not unnecessary_tests:
                    st.markdown("""<div class="alert-green"><p style="margin:0;"><span style="font-weight: 600;">Alle Empfehlungen befolgt</span></p></div>""", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True) 
        st.markdown('</div>', unsafe_allow_html=True)
        
        # --- Final Buttons ---
        col_back, col_submit = st.columns(2)
        with col_back:
            st.button("Zurück zur Diagnose", on_click=prev_step)
        with col_submit:
            st.markdown('<div class="green-button">', unsafe_allow_html=True)
            st.button("Fall speichern", on_click=handle_submit, disabled=len(st.session_state.selected_tests) == 0, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.warning("Keine Empfehlung verfügbar. Bitte zur Diagnoseeingabe zurückkehren und korrigieren.", icon="⚠️")

st.markdown('</div>', unsafe_allow_html=True) # Main Container End