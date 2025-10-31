"""
Setup script to initialize the Medical AI Assistant system
"""
import os
import sys
from pathlib import Path


def setup_project():
    """Run complete setup process"""
    print("=" * 60)
    print("Medical AI Assistant - Setup Script")
    print("=" * 60)
    
    # Step 1: Create patient data
    print("\n[1/4] Generating patient discharge reports...")
    try:
        from create_patient_data import generate_all_patients
        import json
        
        patients = generate_all_patients(30)
        json_path = "data/patient_reports.json"
        
        with open(json_path, "w") as f:
            json.dump(patients, f, indent=2)
        
        print(f"✓ Generated {len(patients)} patient reports")
    except Exception as e:
        print(f"✗ Error generating patient data: {e}")
        return False
    
    # Step 2: Initialize database
    print("\n[2/4] Initializing patient database...")
    try:
        from database import PatientDatabase
        
        db = PatientDatabase()
        json_path = "data/patient_reports.json"
        
        if os.path.exists(json_path):
            count = db.load_from_json(json_path)
            print(f"✓ Loaded {count} patients into database")
        else:
            print("✗ Patient reports file not found")
            return False
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return False
    
    # Step 3: Check environment variables
    print("\n[3/4] Checking environment variables...")
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("⚠ Warning: GROQ_API_KEY not found in .env file")
        print("   Please create a .env file with your Groq API key:")
        print("   GROQ_API_KEY=your_api_key_here")
    else:
        print("✓ GROQ_API_KEY found")
    
    # Step 4: Initialize RAG system (will process PDF on first run)
    print("\n[4/4] Checking RAG system setup...")
    pdf_path = "data/comprehensive-clinical-nephrology.pdf"
    if os.path.exists(pdf_path):
        print(f"✓ PDF file found: {pdf_path}")
        print("  Note: RAG system will process PDF on first API call")
        print("  This may take several minutes for large PDFs")
    else:
        print(f"✗ PDF file not found: {pdf_path}")
        return False
    
    print("\n" + "=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Ensure you have a .env file with GROQ_API_KEY")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Start the FastAPI backend: python api.py")
    print("4. Start the Streamlit frontend: streamlit run app.py")
    print("\n" + "=" * 60)
    
    return True


if __name__ == "__main__":
    success = setup_project()
    sys.exit(0 if success else 1)

