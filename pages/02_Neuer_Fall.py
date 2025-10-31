# pages/02_Neuer_Fall.py

import streamlit as st
from utils import init_state, custom_css, MTS_CATEGORIES, MTS_COLOR_MAP, create_case, lab_tests, recommendations, diagnoses
import time
from datetime import datetime
import random

st.set_page_config(layout="wide", page_title="Neuer Fall")
init_state()
custom_css()

# --- Zustandsmanagement für serielle Schritte ---
if 'step' not in st.session_state: st.session_state.step = 0
if 'new_case_data' not in st.session_state: st.session_state.new_case_data = {}
if 'selected_tests' not in st.session_state: st.session_state.selected_tests = []
if 'current_recommendation' not in st.session_state: st.session_state.current_recommendation = None
if 'is_analyzing' not in st.session_state: st.session_state.is_analyzing = False


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
        r for r in recommendations 
        if r['diagnosis_name'].lower() == diag.lower() and 
           r['mts_category'] == mts
    ), None)

    if matching_rec:
        st.session_state.current_recommendation = matching_rec
        # Wähle automatisch alle empfohlenen Tests aus
        st.session_state.selected_tests = matching_rec['recommended_tests']
    else:
        st.session_state.current_recommendation = {
            "diagnosis_name": diag,
            "mts_category": mts,
            "recommended_tests": [],
            "mandatory_tests": [],
            "optional_tests": [],
            "rationale": "Keine spezifische Empfehlung für diese Diagnose/MTS-Kategorie gefunden. Bitte manuelle Auswahl."
        }
        st.session_state.selected_tests = []
        
    st.session_state.is_analyzing = False
    next_step() # Geht zu Schritt 6 (Testauswahl)


def toggle_test(test_code):
    """Fügt einen Test hinzu oder entfernt ihn."""
    if test_code in st.session_state.selected_tests:
        st.session_state.selected_tests.remove(test_code)
    else:
        st.session_state.selected_tests.append(test_code)

def handle_submit():
    """Verarbeitet die Speicherung des neuen Falls."""
    rec = st.session_state.current_recommendation
    selected_tests = st.session_state.selected_tests
    
    if not selected_tests:
        st.error("Bitte wählen Sie mindestens einen Test aus.")
        return

    # Analyse der Qualität
    mandatory_tests = rec.get('mandatory_tests', [])
    recommended_set = set(rec.get('recommended_tests', []))
    optional_test_codes = set(rec.get('optional_tests', []))

    missing_tests = [t for t in mandatory_tests if t not in selected_tests]
    unnecessary_tests = [t for t in selected_tests if t not in recommended_set and t not in optional_test_codes]
    
    max_duration = max([t['estimated_duration_minutes'] for t in lab_tests if t['test_code'] in selected_tests], default=0)

    # Datenstruktur erstellen
    case_data = {
        **st.session_state.new_case_data, # Übernimmt alle gesammelten Daten
        "ordered_tests": selected_tests,
        "recommended_tests": rec['recommended_tests'] if rec else [],
        "missing_tests": missing_tests,
        "unnecessary_tests": unnecessary_tests,
        "estimated_total_duration": max_duration,
    }

    # Mutation
    create_case(case_data)
    st.toast("Neuer Fall erfolgreich gespeichert!", icon="✅")
    
    # Zustand zurücksetzen und zum Dashboard navigieren
    st.session_state.step = 0
    st.session_state.new_case_data = {}
    st.session_state.selected_tests = []
    st.session_state.current_recommendation = None
    st.switch_page("app.py")


# --- UI Layout ---
st.markdown('<div class="max-w-4xl mx-auto py-6">', unsafe_allow_html=True) # Main Container

st.page_link("app.py", label="Zurück zum Dashboard", icon="arrow_left")
st.markdown("<h1 style='font-size: 2.25rem; font-weight: 700; color: #0F172A;'>Neuer Fall anlegen</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B;'>Erfassen Sie Patientendaten und Laborempfehlungen</p>", unsafe_allow_html=True)
st.markdown("---")


# --- Progress Bar ---
MAX_STEPS = 6 # (0 bis 5)
st.progress(st.session_state.step / MAX_STEPS, text=f"Schritt {st.session_state.step+1}/{MAX_STEPS}")
st.markdown("<br>", unsafe_allow_html=True)


# --- Step-by-Step Forms ---

# ----------------- STEP 0: Identifikation -----------------
if st.session_state.step == 0:
    with st.form(key="step_0_id_form", clear_on_submit=False):
        st.markdown("### 1. Patientendaten (Identifikation)")
        
        patient_number = st.text_input("Patientennummer", placeholder="Patienten-ID eingeben", 
                                       value=st.session_state.new_case_data.get('patient_number', ''))
        
        col_age, col_gender = st.columns(2)
        with col_age:
            age = st.number_input("Alter (Jahre)", min_value=0, max_value=120, 
                                  value=st.session_state.new_case_data.get('age', 35), step=1)
        with col_gender:
            gender_options = ['Männlich', 'Weiblich', 'Divers']
            gender = st.selectbox("Geschlecht", options=gender_options, 
                                  index=gender_options.index(st.session_state.new_case_data.get('gender', 'Männlich')))
        
        if st.form_submit_button("Weiter zu MTS-Einstufung", type="primary"):
            if patient_number:
                next_step({"patient_number": patient_number, "age": age, "gender": gender})
                st.rerun()
            else:
                st.error("Bitte geben Sie eine Patientennummer ein.")

# ----------------- STEP 1: MTS-Einstufung -----------------
elif st.session_state.step == 1:
    with st.form(key="step_1_mts_form", clear_on_submit=False):
        st.markdown("### 2. Dringlichkeit (MTS-Einstufung)")
        
        mts_category = st.selectbox(
            "MTS-Kategorie wählen", 
            options=MTS_CATEGORIES, 
            index=MTS_CATEGORIES.index(st.session_state.new_case_data.get('mts_category', 'Gelb'))
        )
        
        st.info("Das Manchester-Triage-System (MTS) dient zur systematischen Ersteinschätzung der Behandlungsdringlichkeit.", icon="ℹ️")

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
        st.markdown("### 3. Klinisches Bild (Symptome)")
        
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
        st.markdown("### 4. Vitalparameter")
        
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
    
    st.markdown("### 5. Verdachtsdiagnose & KI-Analyse")
    st.markdown("Geben Sie eine Verdachtsdiagnose ein und lassen Sie sich Laborempfehlungen vorschlagen.")

    st.text_input(
        "Verdachtsdiagnose",
        placeholder="z.B. Akutes Koronarsyndrom",
        key='current_diagnosis_input', # Ein separater Key für das Textfeld im aktuellen Step
        value=diagnosis_input_value,
        help=f"Verfügbare Diagnosen (für Demo): {', '.join([d['diagnosis_name'] for d in diagnoses])}"
    )

    col_back, col_analyze = st.columns(2)
    with col_back:
        st.button("Zurück zu Vitalparametern", on_click=prev_step)
    with col_analyze:
        if st.button("KI-Empfehlung abrufen", type="primary", use_container_width=True, disabled=st.session_state.is_analyzing or not st.session_state.current_diagnosis_input):
            st.session_state.new_case_data['suspected_diagnosis'] = st.session_state.current_diagnosis_input # Aktualisiere Diagnose im Hauptdatensatz
            handle_analyze()
            st.rerun()

    if st.session_state.is_analyzing:
        st.info("Analysiere Falldaten und rufe KI-Empfehlung ab...", icon="⏳")

# ----------------- STEP 5: Testauswahl (KI-Ergebnis) -----------------
elif st.session_state.step == 5:
    st.markdown("### 6. Laborwert-Empfehlung und Auswahl")
    
    recommendation = st.session_state.get('current_recommendation')
    if 'selected_tests' not in st.session_state: st.session_state.selected_tests = []

    if recommendation:
        # --- Empfohlene Laborparameter ---
        st.markdown('<div class="stCard-custom">', unsafe_allow_html=True)
        st.markdown('<div class="stCard-header">Empfohlene Laborparameter (KI-Basis)</div>', unsafe_allow_html=True)
        st.markdown('<div class="stCard-content">', unsafe_allow_html=True)

        if recommendation.get('rationale'):
            st.markdown(f'<div class="alert-blue"><p style="margin: 0;">{recommendation["rationale"]}</p></div>', unsafe_allow_html=True)
        
        recommended_test_codes = set(recommendation.get('recommended_tests', []))
        mandatory_test_codes = set(recommendation.get('mandatory_tests', []))
        optional_test_codes = set(recommendation.get('optional_tests', [])) # Auch hier für die Anzeige

        st.markdown("#### **Empfohlene Tests**", unsafe_allow_html=True)
        st.markdown("Tests, die basierend auf Diagnose und Dringlichkeit vorgeschlagen werden:")
        
        cols_rec = st.columns(3)
        rec_tests_filtered = [test for test in lab_tests if test['test_code'] in recommended_test_codes]
        
        if not rec_tests_filtered:
            st.info("Keine spezifischen Tests empfohlen. Bitte wählen Sie manuell aus den 'Weiteren verfügbaren Tests'.", icon="💡")

        for i, test in enumerate(rec_tests_filtered):
            with cols_rec[i % 3]:
                is_mandatory = test['test_code'] in mandatory_test_codes
                test_label = f"**{test['test_name']}** ({test['test_code']})"
                
                if st.checkbox(
                    test_label,
                    value=test['test_code'] in st.session_state.selected_tests,
                    key=f"rec_test_sel_{test['test_code']}"
                ):
                    if test['test_code'] not in st.session_state.selected_tests:
                        st.session_state.selected_tests.append(test['test_code'])
                else:
                    if test['test_code'] in st.session_state.selected_tests:
                        st.session_state.selected_tests.remove(test['test_code'])
                
                if is_mandatory:
                    st.markdown('<span class="badge-base badge-destructive">Pflicht</span>', unsafe_allow_html=True)
                st.caption(f"Dauer: {test['estimated_duration_minutes']} min")

        # --- Weitere verfügbare Tests (Manuelle Auswahl) ---
        st.markdown("---")
        st.markdown("#### **Weitere verfügbare Tests**", unsafe_allow_html=True)
        st.markdown("Wählen Sie zusätzliche Tests, die Sie für diesen Fall für relevant halten.")
        
        all_other_tests = [test for test in lab_tests if test['test_code'] not in recommended_test_codes]
        
        cols_other = st.columns(3)
        if not all_other_tests:
            st.info("Keine weiteren Tests verfügbar.", icon="ℹ️")

        for i, test in enumerate(all_other_tests):
            with cols_other[i % 3]:
                # Auch optionale Tests können hier sein, aber nicht als 'mandatory'
                is_selected = test['test_code'] in st.session_state.selected_tests
                
                if st.checkbox(
                    f"{test['test_name']} ({test['test_code']})",
                    value=is_selected,
                    key=f"other_test_sel_{test['test_code']}"
                ):
                    if test['test_code'] not in st.session_state.selected_tests:
                        st.session_state.selected_tests.append(test['test_code'])
                else:
                    if test['test_code'] in st.session_state.selected_tests:
                        st.session_state.selected_tests.remove(test['test_code'])
                st.caption(f"Dauer: {test['estimated_duration_minutes']} min")


        st.markdown('</div>', unsafe_allow_html=True) # End stCard-content
        st.markdown('</div>', unsafe_allow_html=True) # End stCard-custom
        
        # --- Analyse & Qualitätsprüfung (Block 3) ---
        selected_tests = st.session_state.selected_tests
        
        if selected_tests:
            missing_tests = [t for t in mandatory_test_codes if t not in selected_tests]
            unnecessary_tests = [t for t in selected_tests if t not in recommended_test_codes and t not in optional_test_codes]
            
            st.markdown('<div class="stCard-custom">', unsafe_allow_html=True)
            st.markdown('<div class="stCard-header">Analyse & Qualitätsprüfung</div>', unsafe_allow_html=True)
            st.markdown('<div class="stCard-content">', unsafe_allow_html=True)
            
            # Alerts
            if missing_tests:
                 st.markdown(f"""<div class="alert-red"><p style="margin:0;"><span style="font-weight: 600;">Fehlende Pflicht-Tests:</span> <span style="margin-left: 0.5rem;">{', '.join(missing_tests)}</span></p></div>""", unsafe_allow_html=True)
            if unnecessary_tests:
                 st.markdown(f"""<div class="alert-amber"><p style="margin:0;"><span style="font-weight: 600;">Möglicherweise überflüssig:</span> <span style="margin-left: 0.5rem;">{', '.join(unnecessary_tests)}</span></p></div>""", unsafe_allow_html=True)
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
            st.button("Fall speichern", on_click=handle_submit, disabled=len(selected_tests) == 0, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.warning("Keine Empfehlung verfügbar oder Analyse nicht abgeschlossen. Gehen Sie einen Schritt zurück, um eine Diagnose einzugeben.", icon="⚠️")
        if st.button("Zurück zur Diagnoseeingabe", key="back_from_no_rec"):
            st.session_state.step = 4
            st.rerun()

# ----------------- Fallback für unerwarteten Zustand -----------------
else:
    st.error("Ein unerwarteter Fehler ist aufgetreten oder der Prozess wurde unterbrochen. Bitte neu starten.", icon="🚨")
    if st.button("Neustart des Prozesses"):
        st.session_state.step = 0
        st.session_state.new_case_data = {}
        st.session_state.selected_tests = []
        st.session_state.current_recommendation = None
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True) # Main Container End