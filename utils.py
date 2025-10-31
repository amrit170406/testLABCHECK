# utils.py

import streamlit as st
import pandas as pd
from datetime import datetime
import random
import uuid

# --- Datenmodelle (für Referenz) ---
MTS_CATEGORIES = ['Rot', 'Orange', 'Gelb', 'Grün', 'Blau']
LABTEST_CATEGORIES = ['Hämatologie', 'Klinische Chemie', 'Gerinnung', 'Immunologie', 'Mikrobiologie']
URGENCY_LEVELS = ['Standard', 'Dringend', 'Notfall']

# --- Dummy Data Generator ---
def _generate_initial_data():
    """Erzeugt initiale Listen für LabTests, Diagnoses und Recommendations."""
    
    # 1. Lab Tests
    lab_tests_data = [
        {"id": str(uuid.uuid4()), "test_name": "Troponin T", "test_code": "TROP", "category": "Klinische Chemie", "estimated_duration_minutes": 30, "urgency_level": "Notfall", "unit": "ng/ml", "normal_range": "0-14"},
        {"id": str(uuid.uuid4()), "test_name": "C-reaktives Protein", "test_code": "CRP", "category": "Klinische Chemie", "estimated_duration_minutes": 45, "urgency_level": "Dringend", "unit": "mg/L", "normal_range": "<5"},
        {"id": str(uuid.uuid4()), "test_name": "Kreatinkinase", "test_code": "CK", "category": "Klinische Chemie", "estimated_duration_minutes": 20, "urgency_level": "Dringend", "unit": "U/L", "normal_range": "30-200"},
        {"id": str(uuid.uuid4()), "test_name": "Großes Blutbild", "test_code": "BB", "category": "Hämatologie", "estimated_duration_minutes": 60, "urgency_level": "Standard", "unit": "N/A", "normal_range": "N/A"},
        {"id": str(uuid.uuid4()), "test_name": "D-Dimere", "test_code": "DD", "category": "Gerinnung", "estimated_duration_minutes": 35, "urgency_level": "Dringend", "unit": "ng/ml", "normal_range": "<500"},
        {"id": str(uuid.uuid4()), "test_name": "Blutgasanalyse", "test_code": "BGA", "category": "Klinische Chemie", "estimated_duration_minutes": 15, "urgency_level": "Notfall", "unit": "N/A", "normal_range": "N/A"},
    ]

    # 2. Recommendations
    recommendations_data = [
        {"id": str(uuid.uuid4()), "diagnosis_name": "Akutes Koronarsyndrom", "mts_category": "Rot", "recommended_tests": ["TROP", "CK", "BGA"], "mandatory_tests": ["TROP", "CK"], "optional_tests": ["CRP"], "rationale": "Typisches Set für ACS im Notfall"},
        {"id": str(uuid.uuid4()), "diagnosis_name": "Pneumonie", "mts_category": "Gelb", "recommended_tests": ["BB", "CRP", "BGA"], "mandatory_tests": ["BB", "CRP"], "optional_tests": [], "rationale": "Entzündungsparameter und respiratorischer Status"},
        {"id": str(uuid.uuid4()), "diagnosis_name": "Tiefe Venenthrombose", "mts_category": "Orange", "recommended_tests": ["DD"], "mandatory_tests": ["DD"], "optional_tests": ["BB"], "rationale": "Ausschluss oder Bestätigung einer TVT"},
    ]

    # 3. Diagnoses (simplified)
    diagnoses_data = [
        {"id": str(uuid.uuid4()), "diagnosis_name": "Akutes Koronarsyndrom", "category": "Kardiovaskulär"},
        {"id": str(uuid.uuid4()), "diagnosis_name": "Lungenembolie", "category": "Respiratorisch"},
        {"id": str(uuid.uuid4()), "diagnosis_name": "Pneumonie", "category": "Respiratorisch"},
        {"id": str(uuid.uuid4()), "diagnosis_name": "Tiefe Venenthrombose", "category": "Kardiovaskulär"},
        {"id": str(uuid.uuid4()), "diagnosis_name": "Appendizitis", "category": "Gastrointestinal"},
        {"id": str(uuid.uuid4()), "diagnosis_name": "Sepsis", "category": "Infektiös"},
    ]

    # 4. Patient Cases
    cases_data = []
    
    # Simuliere 5 Fälle
    for i in range(5):
        rec = random.choice(recommendations_data)
        ordered_tests = random.sample(rec['recommended_tests'], k=random.randint(1, len(rec['recommended_tests'])))
        
        # Calculate max duration
        max_duration = max([t['estimated_duration_minutes'] for t in lab_tests_data if t['test_code'] in ordered_tests], default=0)
        
        # Determine missing/unnecessary tests
        missing = [t for t in rec['mandatory_tests'] if t not in ordered_tests]
        unnecessary = [t for t in ordered_tests if t not in rec['recommended_tests']] # Simplified, should only be unnecessary if *not* in recommended

        cases_data.append({
            "id": str(uuid.uuid4()),
            "case_number": f"2025-{i+1:02}", # ANGEPASST: Fortlaufende Fallnummerierung
            "mts_category": rec['mts_category'],
            "suspected_diagnosis": rec['diagnosis_name'],
            "ordered_tests": ordered_tests,
            "recommended_tests": rec['recommended_tests'],
            "missing_tests": missing,
            "unnecessary_tests": unnecessary,
            "estimated_total_duration": max_duration,
            "created_date": (datetime.now() - pd.Timedelta(days=random.randint(0, 7), minutes=random.randint(0, 1440))).isoformat(),
            # Hinzugefügte neue Felder (Dummy-Werte)
            "patient_number": f"PN{random.randint(1000, 9999)}",
            "age": random.randint(18, 90),
            "gender": random.choice(['Männlich', 'Weiblich']),
            "symptoms": "Brustschmerz, Kurzatmigkeit", # Vereinfacht, könnte komplexer sein
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

# --- Zustandsinitialisierung (ersetzt useQuery initialData) ---
def init_state():
    if 'data_initialized' not in st.session_state:
        data = _generate_initial_data()
        st.session_state.lab_tests = data['lab_tests']
        st.session_state.recommendations = data['recommendations']
        st.session_state.diagnoses = data['diagnoses']
        st.session_state.patient_cases = data['patient_cases']
        st.session_state.data_initialized = True
        
        # NEU: Initialisierung des Fallzählers
        latest_case_num = 0
        if st.session_state.patient_cases:
            try:
                # Extrahiere die höchste Nummer (z.B. '05' aus '2025-05')
                latest_case_num = max([int(c['case_number'].split('-')[-1]) for c in st.session_state.patient_cases if '-' in c['case_number']])
            except:
                pass # Falls das Format nicht passt
        st.session_state.case_counter = latest_case_num
        
    if 'edit_dialog_open' not in st.session_state:
        st.session_state.edit_dialog_open = False
    if 'new_rec_dialog_open' not in st.session_state:
        st.session_state.new_rec_dialog_open = False
    if 'new_test_dialog_open' not in st.session_state:
        st.session_state.new_test_dialog_open = False

# --- CRUD Funktionen (ersetzen useMutation) ---

# Patient Cases
def create_case(data):
    """Generiert die fortlaufende Fallnummer und speichert den Fall."""
    st.session_state.case_counter += 1
    new_case_number = f"2025-{st.session_state.case_counter:02}"
    
    data['id'] = str(uuid.uuid4())
    data['created_date'] = datetime.now().isoformat()
    data['case_number'] = new_case_number # Setze die fortlaufende Nummer
    st.session_state.patient_cases.append(data)

def update_case(case_id, data):
    for i, case in enumerate(st.session_state.patient_cases):
        if case['id'] == case_id:
            # Clean up unwanted keys from React code (id, date, etc.)
            for key in ['id', 'created_date', 'updated_date', 'created_by']:
                if key in data:
                    del data[key]
            
            # Update the case
            st.session_state.patient_cases[i] = {**case, **data}
            return True
    return False

def delete_case(case_id):
    st.session_state.patient_cases = [c for c in st.session_state.patient_cases if c['id'] != case_id]

# Lab Tests
def create_lab_test(data):
    data['id'] = str(uuid.uuid4())
    data['estimated_duration_minutes'] = int(data['estimated_duration_minutes'])
    st.session_state.lab_tests.append(data)

def delete_lab_test(test_id):
    st.session_state.lab_tests = [t for t in st.session_state.lab_tests if t['id'] != test_id]

# Recommendations
def create_recommendation(data):
    data['id'] = str(uuid.uuid4())
    st.session_state.recommendations.append(data)

def delete_recommendation(rec_id):
    st.session_state.recommendations = [r for r in st.session_state.recommendations if r['id'] != rec_id]

# --- Styling Helper ---
def custom_css():
    """Definiert das moderne, professionelle CSS für die Streamlit-App."""
    
    st.markdown("""
    <style>
    /* Allgemeine Layout- und Farbanpassungen */
    .stApp {
        background: linear-gradient(to bottom right, #f8fafc, #eff6ff, #f8fafc); /* bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 */
    }
    .stButton > button {
        border-radius: 0.5rem; /* rounded-lg */
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    
    /* Header/Top-Level Anpassungen */
    .st-emotion-cache-18ni7ap { /* st-Header */
        display: none;
    }
    .st-emotion-cache-1wb9q3v { /* Main block */
        padding-top: 0 !important;
    }
    .main-header {
        background-color: white;
        border-bottom: 1px solid #E2E8F0;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        padding: 1.5rem 3rem; /* px-6 py-8 */
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    /* Karten-Styling (ersetzt Shadcn Card) */
    .stCard-custom {
        background-color: white;
        border-radius: 0.75rem; /* rounded-xl */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); /* shadow-lg */
        border: none;
        margin-bottom: 1.5rem;
    }
    .stCard-header {
        border-bottom: 1px solid #F1F5F9; /* slate-100 */
        padding: 1rem 1.5rem;
        font-size: 1.25rem; /* text-xl */
        font-weight: 700; /* font-bold */
        color: #0F172A; /* slate-900 */
    }
    .stCard-content {
        padding: 1.5rem;
    }

    /* Stat Cards (ersetzt Shadcn CardContent) */
    .stat-card {
        background-color: white;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .stat-title {
        color: #64748B; /* slate-500 */
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.25rem;
    }
    .stat-value {
        color: #0F172A; /* slate-900 */
        font-size: 2.25rem;
        font-weight: 700;
    }
    .stat-icon {
        position: absolute;
        top: 1.5rem;
        right: 1.5rem;
        width: 48px;
        height: 48px;
        border-radius: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Links Cards */
    .link-card-blue {
        background: linear-gradient(to bottom right, #3B82F6, #2563EB);
        color: white;
        border-radius: 0.75rem;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3), 0 4px 6px -2px rgba(37, 99, 235, 0.15);
        padding: 1.5rem;
        transition: all 0.3s;
    }
    .link-card-green {
        background: linear-gradient(to bottom right, #10B981, #059669);
        color: white;
        border-radius: 0.75rem;
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3), 0 4px 6px -2px rgba(16, 185, 129, 0.15);
        padding: 1.5rem;
        transition: all 0.3s;
    }
    
    /* Buttons */
    .blue-button button {
        background-color: #2563EB !important; /* blue-600 */
        color: white !important;
    }
    .blue-button button:hover {
        background-color: #1D4ED8 !important; /* blue-700 */
    }
    .green-button button {
        background-color: #10B981 !important; /* green-600 */
        color: white !important;
    }
    .green-button button:hover {
        background-color: #059669 !important; /* green-700 */
    }
    .red-button button {
        color: #DC2626 !important; /* red-600 */
    }

    /* Alerts (ersetzt Shadcn Alert) */
    .alert-red {
        background-color: #FEF2F2; /* red-50 */
        border: 1px solid #FCA5A5; /* red-300 */
        color: #B91C1C; /* red-700 */
        padding: 1rem;
        border-radius: 0.5rem;
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    .alert-amber {
        background-color: #FFFBEB; /* amber-50 */
        border: 1px solid #FCD34D; /* amber-300 */
        color: #D97706; /* amber-700 */
        padding: 1rem;
        border-radius: 0.5rem;
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    .alert-green {
        background-color: #F0FFF4; /* green-50 */
        border: 1px solid #A7F3D0; /* green-300 */
        color: #059669; /* green-700 */
        padding: 1rem;
        border-radius: 0.5rem;
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    .alert-blue {
        background-color: #EFF6FF; /* blue-50 */
        border: 1px solid #93C5FD; /* blue-300 */
        color: #1D4ED8; /* blue-700 */
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }

    /* Badges (ersetzt Shadcn Badge) */
    .badge-base {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.5rem;
        border-radius: 0.375rem;
        display: inline-flex;
        align-items: center;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .badge-red { background-color: #FEE2E2; color: #DC2626; }
    .badge-blue { background-color: #DBEAFE; color: #2563EB; }
    .badge-green { background-color: #D1FAE5; color: #059669; }
    .badge-purple { background-color: #EDE9FE; color: #7C3AED; }
    .badge-amber { background-color: #FFFBEB; color: #D97706; }
    .badge-destructive { background-color: #FEE2F2; color: #DC2626; } /* Equivalent to red */
    .badge-outline { border: 1px solid #D1D5DB; color: #4B5563; background-color: white; }
    .badge-slate { background-color: #F1F5F9; color: #475569; }
    
    /* Case Item Styling */
    .case-item {
        border: 1px solid #E2E8F0;
        border-radius: 0.75rem;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: white;
        transition: all 0.2s;
    }
    .case-item:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Fix für Selectbox und Input */
    .stSelectbox, .stTextInput, .stNumberInput, .stTextArea {
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
    .stForm > div:last-child {
        margin-top: 1.5rem;
    }
    
    /* Icon Sizing for Streamlit's Lucide */
    .stIcon {
        width: 1rem;
        height: 1rem;
    }

    </style>
    """, unsafe_allow_html=True)

# --- Icon Helper (Streamlit Icons) ---
ACTIVITY_SVG = """
<svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="w-7 h-7 text-white" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
"""

# Mapping für MTS-Kategorien
MTS_COLOR_MAP = {
    'Rot': 'background-color: #EF4444;',
    'Orange': 'background-color: #F97316;',
    'Gelb': 'background-color: #FACC15;',
    'Grün': 'background-color: #10B981;',
    'Blau': 'background-color: #3B82F6;'
}

# Call init_state to load data before anything else
init_state()