"""
Script to generate 25+ dummy patient discharge reports
"""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict

# Sample data pools
first_names = [
    "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Jessica",
    "William", "Ashley", "James", "Amanda", "Christopher", "Melissa", "Daniel",
    "Nicole", "Matthew", "Michelle", "Anthony", "Kimberly", "Mark", "Amy",
    "Donald", "Angela", "Steven", "Lisa", "Paul", "Nancy", "Andrew", "Karen"
]

last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young"
]

diagnoses = [
    "Chronic Kidney Disease Stage 3",
    "Chronic Kidney Disease Stage 4",
    "Acute Kidney Injury",
    "Nephrotic Syndrome",
    "Diabetic Nephropathy",
    "Hypertensive Nephropathy",
    "Glomerulonephritis",
    "Polycystic Kidney Disease",
    "Kidney Transplant Follow-up",
    "Renal Artery Stenosis",
    "Interstitial Nephritis",
    "Kidney Stones",
    "Nephritis",
    "Renal Failure",
    "Proteinuria"
]

medications = [
    ["Lisinopril 10mg daily", "Furosemide 20mg twice daily"],
    ["Amlodipine 5mg daily", "Spironolactone 25mg daily", "Metformin 500mg twice daily"],
    ["Losartan 50mg daily", "Chlorthalidone 25mg daily"],
    ["Enalapril 10mg twice daily", "Bumetanide 1mg daily"],
    ["Ramipril 5mg daily", "Hydrochlorothiazide 12.5mg daily"],
    ["Valsartan 80mg daily", "Furosemide 40mg daily"],
    ["Captopril 25mg twice daily", "Triamterene 50mg daily"],
    ["Olmesartan 20mg daily", "Torsemide 20mg daily"],
    ["Prednisone 20mg daily", "Tacrolimus 2mg twice daily"],
    ["Mycophenolate 1000mg twice daily", "Cyclosporine 150mg twice daily"]
]

dietary_restrictions = [
    "Low sodium (2g/day), fluid restriction (1.5L/day)",
    "Low sodium (1.5g/day), low potassium, fluid restriction (2L/day)",
    "Low sodium (2g/day), low protein (0.8g/kg/day)",
    "Low sodium (2.5g/day), fluid restriction (1.5L/day)",
    "Low sodium (2g/day), moderate protein restriction",
    "Low sodium (1.5g/day), fluid restriction (2L/day), low phosphorus",
    "Low sodium (2g/day), fluid restriction (1.5L/day), low potassium",
    "Low sodium (2.5g/day), fluid restriction (1L/day)",
    "Low sodium (2g/day), protein restriction (0.6g/kg/day)",
    "Low sodium (2g/day), fluid restriction (2L/day)"
]

warning_signs = [
    "Swelling, shortness of breath, decreased urine output",
    "Chest pain, difficulty breathing, rapid weight gain",
    "Severe headache, vision changes, chest pain",
    "Fever, chills, pain at surgical site (if applicable)",
    "Nausea, vomiting, loss of appetite",
    "Muscle cramps, weakness, confusion",
    "Blood in urine, decreased urine output",
    "High blood pressure, dizziness",
    "Swelling in face, hands, or feet",
    "Excessive fatigue, difficulty concentrating"
]

discharge_instructions = [
    "Monitor blood pressure daily, weigh yourself daily",
    "Take medications as prescribed, follow-up in 1 week",
    "Monitor blood pressure twice daily, limit salt intake",
    "Weigh yourself daily, call if weight increases by more than 2 pounds in 24 hours",
    "Take all medications with food, monitor for side effects",
    "Follow low-sodium diet strictly, keep all follow-up appointments",
    "Monitor blood pressure and weight daily, report any concerns",
    "Take medications at the same time each day, maintain fluid restrictions",
    "Keep a daily log of blood pressure and weight",
    "Avoid NSAIDs, follow dietary restrictions carefully"
]

follow_ups = [
    "Nephrology clinic in 2 weeks",
    "Primary care in 1 week, nephrology in 3 weeks",
    "Nephrology clinic in 1 week",
    "Lab work in 1 week, nephrology follow-up in 2 weeks",
    "Nephrology clinic in 3 weeks",
    "Primary care in 2 weeks",
    "Lab work and nephrology clinic in 2 weeks",
    "Nephrology clinic in 1 month",
    "Follow-up labs in 1 week",
    "Nephrology clinic in 2-3 weeks"
]


def generate_patient_report(index: int) -> Dict:
    """Generate a single dummy patient report"""
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    patient_name = f"{first_name} {last_name}"
    
    # Generate discharge date (within last 30 days)
    days_ago = random.randint(1, 30)
    discharge_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    
    report = {
        "patient_id": f"PT{str(index).zfill(4)}",
        "patient_name": patient_name,
        "discharge_date": discharge_date,
        "primary_diagnosis": random.choice(diagnoses),
        "medications": random.choice(medications),
        "dietary_restrictions": random.choice(dietary_restrictions),
        "follow_up": random.choice(follow_ups),
        "warning_signs": random.choice(warning_signs),
        "discharge_instructions": random.choice(discharge_instructions),
        "age": random.randint(35, 85),
        "gender": random.choice(["Male", "Female", "Other"]),
        "contact_phone": f"555-{random.randint(1000, 9999)}",
        "blood_pressure": f"{random.randint(110, 140)}/{random.randint(70, 90)}",
        "serum_creatinine": round(random.uniform(1.2, 3.5), 2),
        "egfr": random.randint(30, 60)
    }
    
    return report


def generate_all_patients(num_patients: int = 30) -> List[Dict]:
    """Generate multiple patient reports"""
    patients = []
    for i in range(1, num_patients + 1):
        patients.append(generate_patient_report(i))
    return patients


if __name__ == "__main__":
    # Generate 30 patient reports
    patients = generate_all_patients(30)
    
    # Save to JSON file
    with open("data/patient_reports.json", "w") as f:
        json.dump(patients, f, indent=2)
    
    print(f"Generated {len(patients)} patient reports and saved to data/patient_reports.json")
    print(f"Sample patient: {patients[0]['patient_name']} - {patients[0]['primary_diagnosis']}")

