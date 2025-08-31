#!/usr/bin/env python3
"""
Test script to verify patient saving functionality
"""

import pandas as pd
from datetime import datetime

def test_save_patient():
    try:
        # Load current CSV
        df = pd.read_csv('index.csv')
        print(f"📊 Current patients in CSV: {len(df)}")
        
        # Create test patient data
        test_patient_data = {
            'AGE': 65,
            'GENDER': 'Male',
            'BMI': 28.5,
            'BP_S': 140,
            'GLUCOSE': 120,
            'HbA1c': 6.2,
            'CHOLESTEROL': 220,
            'TOTAL_CLAIMS_COST': 3500,
            'MEDICAL_CONDITIONS': ['Diabetes', 'Heart Disease'],
            'EMAIL': 'test@example.com'
        }
        
        # Create test predictions
        test_predictions = {
            'RISK_30D': 45,
            'RISK_60D': 55,
            'RISK_90D': 65,
            'RISK_LABEL': 'Moderate Risk',
            'TOP_3_FEATURES': 'AGE, GLUCOSE, BP_S',
            'AI_RECOMMENDATIONS': 'Endocrinology consultation for diabetes management | Cardiology consultation for cardiovascular health | Regular monitoring recommended'
        }
        
        # Create new patient record
        new_patient = {
            'DESYNPUF_ID': f"NEW_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'AGE': test_patient_data['AGE'],
            'GENDER': 1 if test_patient_data['GENDER'] == 'Male' else 0,
            'RENAL_DISEASE': 1 if 'Kidney Disease' in test_patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'PARTA': 12, 'PARTB': 12, 'HMO': 0, 'PARTD': 12,
            'ALZHEIMER': 1 if 'Alzheimer' in test_patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'HEARTFAILURE': 1 if 'Heart Disease' in test_patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'CANCER': 1 if 'Cancer' in test_patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'PULMONARY': 1 if 'Lung Disease' in test_patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'OSTEOPOROSIS': 1 if 'Osteoporosis' in test_patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'RHEUMATOID': 1 if 'Arthritis' in test_patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'STROKE': 1 if 'Stroke' in test_patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'TOTAL_CLAIMS_COST': test_patient_data['TOTAL_CLAIMS_COST'],
            'IN_ADM': 0, 'OUT_VISITS': 1, 'ED_VISITS': 0, 'RX_ADH': 0.8,
            'BMI': test_patient_data['BMI'],
            'BP_S': test_patient_data['BP_S'],
            'GLUCOSE': test_patient_data['GLUCOSE'],
            'HbA1c': test_patient_data['HbA1c'],
            'CHOLESTEROL': test_patient_data['CHOLESTEROL'],
            'RISK_30D': test_predictions['RISK_30D'],
            'RISK_60D': test_predictions['RISK_60D'],
            'RISK_90D': test_predictions['RISK_90D'],
            'RISK_LABEL': test_predictions['RISK_LABEL'],
            'TOP_3_FEATURES': test_predictions['TOP_3_FEATURES'],
            'AI_RECOMMENDATIONS': test_predictions['AI_RECOMMENDATIONS']
        }
        
        # Add EMAIL column if it doesn't exist
        if 'EMAIL' not in df.columns:
            df['EMAIL'] = ''
        
        # Add EMAIL to new patient data
        new_patient['EMAIL'] = test_patient_data.get('EMAIL', '')
        
        # Append new patient to dataframe
        df = pd.concat([df, pd.DataFrame([new_patient])], ignore_index=True)
        
        # Save back to CSV
        df.to_csv('index.csv', index=False)
        
        print(f"✅ Successfully saved test patient {new_patient['DESYNPUF_ID']} to CSV")
        print(f"📊 Total patients in CSV after save: {len(df)}")
        
        # Verify the save
        df_verify = pd.read_csv('index.csv')
        print(f"🔍 Verification - Total patients in CSV: {len(df_verify)}")
        
        # Check if new patient exists
        new_patients = df_verify[df_verify['DESYNPUF_ID'].str.startswith('NEW_', na=False)]
        print(f"🆕 New patients found: {len(new_patients)}")
        
        if len(new_patients) > 0:
            latest_patient = new_patients.iloc[-1]
            print(f"📋 Latest new patient: {latest_patient['DESYNPUF_ID']}")
            print(f"   Age: {latest_patient['AGE']}, Risk: {latest_patient['RISK_LABEL']}")
            print(f"   AI Recommendations: {latest_patient['AI_RECOMMENDATIONS']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False

if __name__ == "__main__":
    test_save_patient()
