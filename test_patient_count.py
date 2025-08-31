#!/usr/bin/env python3
"""
Test script to verify patient count functionality
"""

import pandas as pd

def test_patient_count():
    try:
        # Load the current dataset
        df = pd.read_csv('index.csv')
        current_count = len(df)
        
        print(f"✅ Current patient count: {current_count}")
        print(f"📊 Dataset shape: {df.shape}")
        
        # Check for new patients
        new_patients = df[df['DESYNPUF_ID'].str.startswith('NEW_', na=False)]
        print(f"🆕 New patients added: {len(new_patients)}")
        
        if len(new_patients) > 0:
            print("\n📋 Recent new patients:")
            for idx, patient in new_patients.tail(5).iterrows():
                print(f"  - {patient['DESYNPUF_ID']}: {patient['AGE']} years, {patient['RISK_LABEL']}")
        
        return current_count
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

if __name__ == "__main__":
    test_patient_count()
