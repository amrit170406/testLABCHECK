# utils.py

import streamlit as st
import pandas as pd
from datetime import datetime
import random
import uuid

# --- Globale Konstanten ---
MTS_CATEGORIES = ['Rot', 'Orange', 'Gelb', 'Grün', 'Blau']
LABTEST_CATEGORIES = ['Hämatologie', 'Klinische Chemie', 'Gerinnung', 'Immunologie', 'Mikrobiologie']
URGENCY_LEVELS = ['Standard', 'Dringend', 'Notfall']
FALLNUMMER_PRÄFIX = "2025" # Das Präfix für die fortlaufende Fallnummer

# --- Dummy Data Generator ---
@st.cache_resource(show_spinner="Lade kritische Daten...")
def _generate_initial_data():
    """Erzeugt robuste Initialdaten für die Anwendung."""
    
    # Lab Tests (1. Datenquelle)
    lab_tests_data = [
        {"id": str(uuid.uuid4()), "test_name": "Troponin T", "test_code": "TROP", "category": "Klinische Chemie", "estimated_duration_minutes": 30, "urgency_level": "Notfall", "unit": "ng/ml", "normal_range": "0-14"},
        {"id": str(uuid.uuid4()), "test_name": "C-reaktives Protein", "test_code": "CRP", "category": "Klinische Chemie", "estimated_duration_minutes": 45, "urgency_level": "Dringend", "unit": "mg/L", "normal_range": "<5"},
        {"id": str(uuid.uuid4()), "test_name": "Kreatinkinase", "test_code": "CK", "category": "Klinische Chemie", "estimated_duration_minutes": 20, "urgency_level": "Dringend", "unit": "U/L", "normal_range": "30-200"},
        {"id": str(uuid.uuid4()), "test_name": "Großes Blutbild", "test_code": "BB", "category": "Hämatologie", "estimated_duration_minutes": 60, "urgency_level": "Standard", "unit": "N/A", "normal_range": "N/A"},
        {"id": str(uuid.uuid4()), "test_name": "D-Dimere", "test_code": "DD", "category": "Gerinnung", "estimated_duration_minutes": 35, "urgency_level": "Notfall", "unit": "ng/ml", "normal_range": "<500"},
        {"id": str(uuid.uuid4()), "test_name": "Blutgasanalyse", "test_code": "BGA", "category": "Klinische Chemie", "estimated_duration_minutes": 15, "urgency_level": "Notfall", "unit": "N/A", "normal_range": "N/A"},
        {"id": str(uuid.uuid4()), "test_name": "Laktat", "test_code": "LAKT", "category": "Klinische Chemie", "estimated_duration_minutes": 15, "urgency_level": "Notfall", "unit": "mmol/L", "normal_range": "<2.0"},
        {"id": str(uuid.uuid4()), "test_name": "Nierenwerte", "test_code": "NIERE", "category": "Klinische Chemie", "estimated_duration_minutes": 30, "urgency_level": "Dringend", "unit": "N/A", "normal_range": "N/A"},
    ]

    # Recommendations (2. Datenquelle)
    recommendations_data = [
        {"id": str(uuid.uuid4()), "diagnosis_name": "Akutes Koronarsyndrom", "mts_category": "Rot", "recommended_tests": ["TROP", "CK", "BGA"], "mandatory_tests": ["TROP", "CK"], "optional_tests": ["CRP"], "rationale": "Typisches Set für ACS im Notfall. Schnelle Herzmarker-Bestimmung."},
        {"id": str(uuid.uuid4()), "diagnosis_name": "Pneumonie", "mts_category": "Gelb", "recommended_tests": ["BB", "CRP", "BGA"], "mandatory_tests": ["BB", "CRP"], "optional_tests": ["LAKT"], "rationale": "Entzündungsparameter und respiratorischer Status bei Verdacht auf Lungenentzündung."},
        {"id": str(uuid.uuid4()), "diagnosis_name": "Lungenembolie", "mts_category": "Orange", "recommended_tests": ["DD", "BGA"], "mandatory_tests": ["DD"], "optional_tests": ["BB"], "rationale": "D-Dimere zum Ausschluss, Atemanalyse aufgrund der Dringlichkeit."},
        {"id": str(uuid.uuid4()), "diagnosis_name": "Sepsis", "mts_category": "Rot", "recommended_tests": ["BB", "CRP", "LAKT", "NIERE"], "mandatory_tests": ["BB", "CRP", "LAKT"], "optional_tests": [], "rationale": "Umfassende Abklärung bei Verdacht auf schwere systemische Infektion."},
    ]

    # Diagnoses (3. Datenquelle)
    diagnoses_data = [
        {"id": str(uuid.uuid4()), "diagnosis_name": "Akutes Koronarsyndrom", "category": "Kardiovaskulär"},
        {"id": str(uuid.uuid4()), "diagnosis_name": "Lungenembolie", "category": "Respiratorisch"},
        {"id": str(uuid.uuid4()), "diagnosis_name": "Pneumonie", "category": "Respiratorisch"},
        {"id": str(uuid.uuid4()), "diagnosis_name": "Sepsis", "category": "Infektiös"},
        {"id": str(uuid.uuid4()), "diagnosis_name": "Akutes Nierenversagen", "category": "Nephrologie"},
    ]
    
    # Patient Cases (4. Datenquelle)
    cases_data = []
    for i in range(5):
        rec = random.choice(recommendations_data)
        ordered_tests = random.sample(rec['recommended_tests'], k=len(rec['recommended_tests']))
        max_duration = max([t['estimated_duration_minutes'] for t in lab_tests_data if t['test_code'] in ordered_tests], default=0)
        missing = [t for t in rec['mandatory_tests'] if t not in ordered_tests]
        unnecessary = [t for t in ordered_tests if t not in (set(rec['recommended_tests']) | set(rec['optional_tests']))]

        cases_data.append({
            "id": str(uuid.uuid4()),
            "case_number": f"{FALLNUMMER_PRÄFIX}-{i+1:02}",
            "mts_category": rec['mts_category'],
            "suspected_diagnosis": rec['diagnosis_name'],
            "ordered_tests": ordered_tests,
            "recommended_tests": rec['recommended_tests'],
            "missing_tests": missing,
            "unnecessary_tests": unnecessary,
            "estimated_total_duration": max_duration,
            "created_date": (datetime.now() - pd.Timedelta(days=random.randint(0, 7), minutes=random.randint(0, 1440))).isoformat(),
            "patient_number": f"PN{random.randint(1000, 9999)}",
            "age": random.randint(18, 90),
            "gender": random.choice(['Männlich', 'Weiblich', 'Divers']),
            "symptoms": "Brustschmerz, Kurzatmigkeit",
            "vitals": {
                "blood_pressure": f"{random.randint(90, 180)}/{random.randint(60, 120)}",
                "temperature": round(random.uniform(36.5, 39.5), 1),
                "heart_rate": random.randint(50, 120),
                "respiratory_rate": random.randint(12, 30),
                "oxygen_saturation": random.randint(90, 100),
                "blood_sugar": random.randint(80, 200)
            }
        })

    return {
        "lab_tests": lab_tests_data,
        "recommendations": recommendations_data,
        "diagnoses": diagnoses_data,
        "patient_cases": cases_data
    }

# --- Zustandsinitialisierung (Start-up) ---
def init_state():
    if 'data_initialized' not in st.session_state:
        data = _generate_initial_data()
        st.session_state.lab_tests = data['lab_tests']
        st.session_state.recommendations = data['recommendations']
        st.session_state.diagnoses = data['diagnoses']
        st.session_state.patient_cases = data['patient_cases']
        st.session_state.data_initialized = True
        
        # Initialisierung des Fallzählers für fortlaufende Nummerierung
        latest_case_num = 0
        if st.session_state.patient_cases:
            try:
                latest_case_num = max([int(c['case_number'].split('-')[-1]) for c in st.session_state.patient_cases if c['case_number'].startswith(FALLNUMMER_PRÄFIX)])
            except:
                pass
        st.session_state.case_counter = latest_case_num
        
    # Initialisierung der UI-Zustände (wichtig für Kompatibilität)
    if 'edit_dialog_open' not in st.session_state: st.session_state.edit_dialog_open = False
    if 'new_rec_dialog_open' not in st.session_state: st.session_state.new_rec_dialog_open = False
    if 'new_test_dialog_open' not in st.session_state: st.session_state.new_test_dialog_open = False
    if 'step' not in st.session_state: st.session_state.step = 0
    if 'new_case_data' not in st.session_state: st.session_state.new_case_data = {}
    if 'selected_tests' not in st.session_state: st.session_state.selected_tests = []
    if 'current_recommendation' not in st.session_state: st.session_state.current_recommendation = None
    if 'is_analyzing' not in st.session_state: st.session_state.is_analyzing = False


# --- CRUD Funktionen (ersetzen useMutation) ---
def create_case(data):
    """Generiert die fortlaufende Fallnummer und speichert den Fall."""
    st.session_state.case_counter += 1
    new_case_number = f"{FALLNUMMER_PRÄFIX}-{st.session_state.case_counter:02}"
    
    data['id'] = str(uuid.uuid4())
    data['created_date'] = datetime.now().isoformat()
    data['case_number'] = new_case_number
    st.session_state.patient_cases.append(data)

def update_case(case_id, data):
    for i, case in enumerate(st.session_state.patient_cases):
        if case['id'] == case_id:
            for key in ['id', 'created_date', 'updated_date', 'created_by']:
                if key in data:
                    del data[key]
            st.session_state.patient_cases[i] = {**case, **data}
            return True
    return False

def delete_case(case_id):
    st.session_state.patient_cases = [c for c in st.session_state.patient_cases if c['id'] != case_id]

def create_lab_test(data):
    data['id'] = str(uuid.uuid4())
    data['estimated_duration_minutes'] = int(data['estimated_duration_minutes'])
    st.session_state.lab_tests.append(data)

def delete_lab_test(test_id):
    st.session_state.lab_tests = [t for t in st.session_state.lab_tests if t['id'] != test_id]

def create_recommendation(data):
    data['id'] = str(uuid.uuid4())
    st.session_state.recommendations.append(data)

def delete_recommendation(rec_id):
    st.session_state.recommendations = [r for r in st.session_state.recommendations if r['id'] != rec_id]


# --- Styling Helper ---

# Mapping für MTS-Kategorien (für Inline-Styling)
MTS_COLOR_MAP = {
    'Rot': '#EF4444',
    'Orange': '#F97316',
    'Gelb': '#FACC15',
    'Grün': '#10B981',
    'Blau': '#3B82F6'
}

# Mapping für Labortest-Kategorien für Badges
LAB_CATEGORIES_BADGE_MAP = {
    'Hämatologie': 'bg-red-100 text-red-800',
    'Klinische Chemie': 'bg-blue-100 text-blue-800',
    'Gerinnung': 'bg-purple-100 text-purple-800',
    'Immunologie': 'bg-green-100 text-green-800',
    'Mikrobiologie': 'bg-amber-100 text-amber-800'
}

def custom_css():
    """Definiert das optimierte, bombastische CSS für die Streamlit-App."""
    
    st.markdown("""
    <style>
    /* 1. Globales Layout und Schriftarten */
    .stApp {
        background: linear-gradient(to bottom right, #f8fafc, #eff6ff, #f8fafc); 
    }
    .st-emotion-cache-18ni7ap { display: none; } /* Header ausblenden */
    .st-emotion-cache-1wb9q3v { padding-top: 0 !important; padding-right: 3rem !important; padding-left: 3rem !important; padding-bottom: 3rem !important; }
    h1, h2, h3, h4, h5 { color: #0F172A; }
    p { color: #475569; }

    /* 2. Header Style */
    .main-header {
        background-color: white;
        border-bottom: 1px solid #E2E8F0;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        padding: 1.5rem 3rem; 
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        position: fixed; /* Fixiere den Header */
        top: 0;
        left: 0;
        z-index: 1000;
    }
    /* Platzhalter für den fixed Header */
    .header-spacer { height: 100px; } 

    /* 3. Button / Primärfarben */
    .stButton > button {
        border-radius: 0.5rem;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .blue-button button { background-color: #2563EB !important; color: white !important; border: none !important; }
    .blue-button button:hover { background-color: #1D4ED8 !important; }
    .green-button button { background-color: #10B981 !important; color: white !important; border: none !important; }
    .green-button button:hover { background-color: #059669 !important; }
    .red-button button { color: #DC2626 !important; border: 1px solid #DC2626 !important; background-color: white !important; }
    .red-button button:hover { background-color: #FEE2E2 !important; }
    
    /* 4. Karten und Container */
    .stCard-custom {
        background-color: white;
        border-radius: 0.75rem; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); 
        border: none;
        margin-bottom: 1.5rem;
    }
    .stCard-header {
        border-bottom: 1px solid #F1F5F9; 
        padding: 1rem 1.5rem;
        font-size: 1.25rem;
        font-weight: 700; 
        color: #0F172A;
    }
    .stCard-content {
        padding: 1.5rem;
    }

    /* 5. Stat Cards */
    .stat-card {
        background-color: white;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        padding: 1.5rem;
        position: relative;
        height: 100%;
    }
    .stat-value { color: #0F172A; font-size: 2.25rem; font-weight: 700; margin-bottom: 0.5rem; }
    .stat-title { color: #64748B; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem; }
    
    /* 6. Alerts & Badges */
    .alert-red { background-color: #FEF2F2; border: 1px solid #FCA5A5; color: #B91C1C; padding: 1rem; border-radius: 0.5rem; }
    .alert-amber { background-color: #FFFBEB; border: 1px solid #FCD34D; color: #D97706; padding: 1rem; border-radius: 0.5rem; }
    .alert-green { background-color: #F0FFF4; border: 1px solid #A7F3D0; color: #059669; padding: 1rem; border-radius: 0.5rem; }
    .alert-blue { background-color: #EFF6FF; border: 1px solid #93C5FD; color: #1D4ED8; padding: 1rem; border-radius: 0.5rem; }
    
    .badge-base { font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.5rem; border-radius: 0.375rem; display: inline-flex; margin-right: 0.5rem; margin-bottom: 0.5rem; }
    
    /* 7. Quick Link Cards (OPTIMIERT FÜR UNTERSCHIEDLICHE INHALTSGRÖSSEN) */
    .link-card-btn > button {
        text-align: left;
        height: 100%;
        min-height: 140px; /* Einheitliche Höhe erzwingen */
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: center;
        line-height: 1.4;
        transition: all 0.3s;
    }
    /* Überschreiben spezifischer Button-Styles für die Link-Karten */
    div[data-testid="stButton"] > button[key*="link_card"] {
        padding: 1.5rem;
        font-size: 1.25rem; 
        font-weight: 700;
        white-space: pre-wrap; /* Zeilenumbrüche im Text behalten */
    }
    div[data-testid="stButton"] > button[key*="link_card"] > div > span:last-child {
        font-size: 1rem;
        font-weight: 400;
        margin-top: 0.5rem;
        display: block;
    }
    .link-card-blue > button { background: linear-gradient(to bottom right, #3B82F6, #2563EB); color: white; box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3); }
    .link-card-green > button { background: linear-gradient(to bottom right, #10B981, #059669); color: white; box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3); }
    .link-card-blue > button:hover, .link-card-green > button:hover { transform: translateY(-3px); box-shadow: 0 15px 25px -5px rgba(0, 0, 0, 0.2); }


    </style>
    """, unsafe_allow_html=True)

# Call init_state to load data before anything else
init_state()