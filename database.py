"""
SQLite database setup for patient discharge reports
"""
import sqlite3
import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class PatientDatabase:
    """Handles SQLite database operations for patient discharge reports"""
    
    def __init__(self, db_path: str = "patient_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                patient_name TEXT NOT NULL,
                discharge_date TEXT NOT NULL,
                primary_diagnosis TEXT NOT NULL,
                medications TEXT NOT NULL,
                dietary_restrictions TEXT,
                follow_up TEXT,
                warning_signs TEXT,
                discharge_instructions TEXT,
                age INTEGER,
                gender TEXT,
                contact_phone TEXT,
                blood_pressure TEXT,
                serum_creatinine REAL,
                egfr INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def insert_patient(self, patient_data: Dict):
        """Insert a single patient record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO patients (
                    patient_id, patient_name, discharge_date, primary_diagnosis,
                    medications, dietary_restrictions, follow_up, warning_signs,
                    discharge_instructions, age, gender, contact_phone,
                    blood_pressure, serum_creatinine, egfr
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patient_data.get("patient_id"),
                patient_data.get("patient_name"),
                patient_data.get("discharge_date"),
                patient_data.get("primary_diagnosis"),
                json.dumps(patient_data.get("medications", [])),
                patient_data.get("dietary_restrictions"),
                patient_data.get("follow_up"),
                patient_data.get("warning_signs"),
                patient_data.get("discharge_instructions"),
                patient_data.get("age"),
                patient_data.get("gender"),
                patient_data.get("contact_phone"),
                patient_data.get("blood_pressure"),
                patient_data.get("serum_creatinine"),
                patient_data.get("egfr")
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_patient_by_name(self, name: str) -> Optional[Dict]:
        """Retrieve patient by exact name match"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM patients WHERE patient_name = ?", (name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            patient_dict = dict(row)
            patient_dict["medications"] = json.loads(patient_dict["medications"])
            return patient_dict
        return None
    
    def search_patients_by_name(self, name: str) -> List[Dict]:
        """Search patients by partial name match"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM patients WHERE patient_name LIKE ?", (f"%{name}%",))
        rows = cursor.fetchall()
        conn.close()
        
        patients = []
        for row in rows:
            patient_dict = dict(row)
            patient_dict["medications"] = json.loads(patient_dict["medications"])
            patients.append(patient_dict)
        
        return patients
    
    def get_all_patients(self) -> List[Dict]:
        """Get all patients"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM patients")
        rows = cursor.fetchall()
        conn.close()
        
        patients = []
        for row in rows:
            patient_dict = dict(row)
            patient_dict["medications"] = json.loads(patient_dict["medications"])
            patients.append(patient_dict)
        
        return patients
    
    def load_from_json(self, json_path: str):
        """Load patient data from JSON file into database"""
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        
        with open(json_path, "r") as f:
            patients = json.load(f)
        
        inserted = 0
        for patient in patients:
            if self.insert_patient(patient):
                inserted += 1
        
        return inserted


if __name__ == "__main__":
    # Initialize database and load patient data
    db = PatientDatabase()
    
    # Check if patient_reports.json exists
    json_path = "data/patient_reports.json"
    if os.path.exists(json_path):
        print(f"Loading patients from {json_path}...")
        count = db.load_from_json(json_path)
        print(f"Loaded {count} patients into database.")
    else:
        print(f"Patient reports file not found at {json_path}")
        print("Please run create_patient_data.py first to generate patient data.")

